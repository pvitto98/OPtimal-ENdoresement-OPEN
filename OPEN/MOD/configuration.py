from __future__ import print_function
import subprocess
import time
import timeit
import os
import threading
import concurrent.futures
import datetime
import iperf3
import datetime
import matplotlib.pyplot as plt
import math
import pickle
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from scipy.stats import poisson
import seaborn as sb
import numpy as np
import psutil
import csv
import glob
import pathlib

dockerComposeFileName = "docker-compose.yml"
containerBridgeInfoFileName = "configurationFiles/container_bridge_info.txt"
delaysFileName = "configurationFiles/delays.txt"
upperbandwidhtFileName = "configurationFiles/upperbandwidth.txt"
lowerBandwidthFileName = "configurationFiles/lowerbandwidth.txt"
outputREPingFileName = "output/REresultPing.txt "
outputValuesPingFileName = "output/valuesPing.txt"
relativeErrorIperfFileName = "output/RelativeErrorIperf.txt"
bandwidthValuesFileName = 'output/BandwidthValues.txt'


ENABLE_NETWORK_CONFIGURATION = True
THREADS = True
PRE_JOIN_THREADS = True
MODE = "htb"

NUM_ORG = 8
C=NUM_ORG+1

MAX_RETRY_TIME = 3

ISSUER=1

DONTSHOWOUTPUT = '> /dev/null 2>&1'
baseName='client'

MODE = "htb"

NUM_ORG = 8
C=NUM_ORG+1

baseName='client'


def cleanEnvironment():
    print("")
    print("[FUNCTION] : cleanEnvironment() invoked")
    for i in range(1,C):
        clientName=baseName+str(i)
        temp = subprocess.Popen(['sudo','docker', 'container', 'stop', clientName], stdout= subprocess.PIPE)
        temp.communicate()

    for i in range(1,C):
        clientName=baseName+str(i)
        temp = subprocess.Popen(['sudo','docker', 'container', 'rm', clientName], stdout= subprocess.PIPE)
        temp.communicate()


    temp = subprocess.Popen(['sudo','docker', 'network', 'rm', 'endorsmentpoliciesthesis_net1'], stdout= subprocess.PIPE)
    temp.communicate()

    temp = subprocess.Popen(['rm', 'docker-compose.yml'], stdout= subprocess.PIPE)
    temp.communicate()

def generateComposerFile():
    print("")
    print("[FUNCTION]: generateComposerFile() invoked")

    dockerComposeFile = open(dockerComposeFileName, 'w+')
    print("version: '3.0'", file = dockerComposeFile)
    print("   ", file = dockerComposeFile)
    print("networks:", file = dockerComposeFile)
    print("  net1:", file = dockerComposeFile)
    print("    driver: bridge", file = dockerComposeFile)
    print("   ", file = dockerComposeFile)
    print("services:", file = dockerComposeFile)
    for i in range(1,C):
        print("  client"+ str(i) +":", file = dockerComposeFile)
        print("    container_name: client"+ str(i), file = dockerComposeFile)
        print("    build: ./client", file = dockerComposeFile)
        print("    tty: true", file = dockerComposeFile)
        print("    networks:", file = dockerComposeFile)
        print("      - net1", file = dockerComposeFile)
        print("    cap_add:", file = dockerComposeFile)
        print("    - NET_ADMIN", file = dockerComposeFile)
        print("   ", file = dockerComposeFile)
    print("[generateComposerFile]: docker-compose file created")

def isAlreadyDeployed(containers):
    cmd1_1 = "docker ps --format {{.Names}}|grep -v \"dev\"|grep -w "
    cmd1_2 = " |cut -d ':' -f 1"
    for value in containers:
        response = getCleanSubProcessOutput(cmd1_1 + value.name + cmd1_2)
        if response != value.name:
             print("FATAL ERROR. YOU MUST RESTART THE NETWORK.")
             exit(0)

def generateContainerBridgeInfoFile():
    #print("")
    #print("[FUNCTION] : generateContainerBridgeInfoFile() invoked")
    containerBridgeInfoFile = open(containerBridgeInfoFileName, 'w+')
    upperbandwidhtFile = open(upperbandwidhtFileName, 'r')
    delaysFile = open(delaysFileName, 'r')
    lowerBandwidthFile = open(lowerBandwidthFileName, 'r')


    containers = []
    cmd1_1 = "docker ps --format {{.Names}}|grep -v \"dev\"|grep -w \"peer0.org"
    cmd1_2 = ".example.com\"|cut -d ':' -f 1"
    cmd2_1 = "docker ps --format {{.ID}}:{{.Names}}|grep -v \"dev\"|grep "
    cmd2_2 = "|cut -d ':' -f 1"
    cmd3_1 = "docker network inspect net_test|grep -v \"dev\"|grep -A3 \"$(echo "
    cmd3_2 = "|cut -d ':' -f 2)\"|grep 'IP'|sed 's/ //g'|cut -d ',' -f 1|cut -d ':' -f 2"
    cmd4_1 = "sudo docker exec $(echo "
    cmd4_2 = "|cut -d ':' -f 2) ip a|grep ${INTF}@|cut -d ':' -f 1"
    #   veth_in_bridge=$(sudo ip a|grep "if${veth_in_container}"|cut -d ":" -f 2|cut -d '@' -f 1|sed "s/ //g")

    cmd5_1 = "sudo ip a|grep 'if"
    cmd5_2 = "'|cut -d ':' -f 2|cut -d '@' -f 1|sed 's/ //g'"
#   container_IP=$(docker network inspect endorsmentpoliciesthesis_net1|grep -A3 \"$(echo $i|cut -d ":" -f 2)\"|grep "IP"|sed "s/ //g"|cut -d "," -f 1|cut -d ":" -f 2)

    for row in upperbandwidhtFile:
        upperbandwidht = row.split(" ")
        break

    upperbandwidhtIndex = 0
    delaysMatrix = np.zeros( (NUM_ORG,NUM_ORG) )
    lowerBandwidthMatrix = np.zeros( (NUM_ORG,NUM_ORG) )
    lowerBandwidthVector = []

    j=0

    i = 0
    for row in delaysFile:
        delays= row.split(" ")
        delaysVector = []
        j=0
        for value in delays:
            if (j!= 0):
                if (value.replace("\n","").isnumeric()):
                        delaysMatrix[i][j-1] = int(value.replace("\n","").replace(" ", ""))
            j=j+1
        i=i+1


    i = 0
    for row in lowerBandwidthFile:
        lowerBandwidth= row.split(" ")
        j=0
        for value in lowerBandwidth:
            if (j!= 0):
                if (value.replace("\n","").isnumeric()):
                        lowerBandwidthMatrix[i][j-1] = int(value.replace("\n","").replace(" ", ""))
            j=j+1
        i=i+1


    for i in range(0,NUM_ORG):
        container_name = getCleanSubProcessOutput(cmd1_1 + str(i+1) + cmd1_2)
        #print("container_name " + container_name)
        cmd = container_name + cmd2_2
        container_ID = getCleanSubProcessOutput(cmd2_1 + container_name + cmd2_2)
        #print("container_ID " + container_ID)
        container_IP = getCleanSubProcessOutput(cmd3_1 + container_name + cmd3_2)
        #print("container_IP " + container_IP)
        veth_in_container = getCleanSubProcessOutput(cmd4_1 + container_name + cmd4_2)
        #print("veth_in_container " + veth_in_container)
        veth_in_bridge = getCleanSubProcessOutput (cmd5_1 + str(veth_in_container) + cmd5_2)
        #print("veth_in_bridge " + veth_in_bridge)

        for a in range(0,NUM_ORG):
            delaysVector.append(delaysMatrix[i][a])
            lowerBandwidthVector.append(lowerBandwidthMatrix[i][a])

        #print(container_name + " " + lowerBandwidthVector)


        containers.append(Container(container_ID, container_name, veth_in_bridge, container_IP, delaysVector, int(upperbandwidht[upperbandwidhtIndex]), lowerBandwidthVector))
        upperbandwidhtIndex=upperbandwidhtIndex+1
        delaysVector=[]
        lowerBandwidthVector = []


    #for val in containers:
    #    a0 = os.popen("sudo docker exec "+ val.name +" apk update").read()
    #    a1 = os.popen("sudo docker exec "+ val.name +" apk upgrade").read()
    #    a2 = os.popen("sudo docker exec "+ val.name +" apk add iperf").read()
    #    print(val.toString())



        #a0 = subprocess.Popen(["sudo", "docker", "exec", val.name, "apk", "update"], shell=True, stderr=subprocess.STDOUT)
        #print(str(a0.communicate()[0])
        #a1 = subprocess.Popen(["sudo", "docker", "exec", val.name, "apk", "upgrade"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #print(str(a1.communicate()[0])
        #a2 = subprocess.Popen(["sudo", "docker", "exec", val.name, "apk", "add",  "iperf3"], shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        #print(str(a2.communicate()[0])


    delaysFile.close()
    containerBridgeInfoFile.close()
    return containers

def generateContainerBridgeInfoFile_SmartContract():
    #print("")
    #print("[FUNCTION] : generateContainerBridgeInfoFile() invoked")
    containerBridgeInfoFile = open(containerBridgeInfoFileName, 'w+')
    upperbandwidhtFile = open(upperbandwidhtFileName, 'r')
    delaysFile = open(delaysFileName, 'r')
    lowerBandwidthFile = open(lowerBandwidthFileName, 'r')


    containers = []
    cmd1_1 = "docker ps --format {{.Names}} | grep -E \bdev-peer0.org "
    cmd1_2 = "|cut -d ':' -f 1"
    cmd2_1 = "docker ps --format {{.ID}}:{{.Names}}|grep -v \"dev\"|grep "
    cmd2_2 = "|cut -d ':' -f 1"
    cmd3_1 = "docker network inspect net_test|grep -v \"dev\"|grep -A3 \"$(echo "
    cmd3_2 = "|cut -d ':' -f 2)\"|grep 'IP'|sed 's/ //g'|cut -d ',' -f 1|cut -d ':' -f 2"
    cmd4_1 = "sudo docker exec $(echo "
    cmd4_2 = "|cut -d ':' -f 2) ip a|grep ${INTF}@|cut -d ':' -f 1"
    #   veth_in_bridge=$(sudo ip a|grep "if${veth_in_container}"|cut -d ":" -f 2|cut -d '@' -f 1|sed "s/ //g")

    cmd5_1 = "sudo ip a|grep 'if"
    cmd5_2 = "'|cut -d ':' -f 2|cut -d '@' -f 1|sed 's/ //g'"
#   container_IP=$(docker network inspect endorsmentpoliciesthesis_net1|grep -A3 \"$(echo $i|cut -d ":" -f 2)\"|grep "IP"|sed "s/ //g"|cut -d "," -f 1|cut -d ":" -f 2)

    for row in upperbandwidhtFile:
        upperbandwidht = row.split(" ")
        break

    upperbandwidhtIndex = 0
    delaysMatrix = np.zeros( (NUM_ORG,NUM_ORG) )
    lowerBandwidthMatrix = np.zeros( (NUM_ORG,NUM_ORG) )
    lowerBandwidthVector = []

    j=0

    i = 0
    for row in delaysFile:
        delays= row.split(" ")
        delaysVector = []
        j=0
        for value in delays:
            if (j!= 0):
                if (value.replace("\n","").isnumeric()):
                        delaysMatrix[i][j-1] = int(value.replace("\n","").replace(" ", ""))
            j=j+1
        i=i+1


    i = 0
    for row in lowerBandwidthFile:
        lowerBandwidth= row.split(" ")
        j=0
        for value in lowerBandwidth:
            if (j!= 0):
                if (value.replace("\n","").isnumeric()):
                        lowerBandwidthMatrix[i][j-1] = int(value.replace("\n","").replace(" ", ""))
            j=j+1
        i=i+1
        containers_name = ["dev-peer0.org3.example.com-basic_1.0-9d0b67fed5b00f1dec364b2a4b5d0c5e7709050ed3cae84bf01cd4fe94b9b21b",
"dev-peer0.org6.example.com-basic_1.0-9d0b67fed5b00f1dec364b2a4b5d0c5e7709050ed3cae84bf01cd4fe94b9b21b",
"dev-peer0.org4.example.com-basic_1.0-9d0b67fed5b00f1dec364b2a4b5d0c5e7709050ed3cae84bf01cd4fe94b9b21b",
"dev-peer0.org1.example.com-basic_1.0-9d0b67fed5b00f1dec364b2a4b5d0c5e7709050ed3cae84bf01cd4fe94b9b21b",
"dev-peer0.org7.example.com-basic_1.0-9d0b67fed5b00f1dec364b2a4b5d0c5e7709050ed3cae84bf01cd4fe94b9b21b",
"dev-peer0.org5.example.com-basic_1.0-9d0b67fed5b00f1dec364b2a4b5d0c5e7709050ed3cae84bf01cd4fe94b9b21b",
"dev-peer0.org8.example.com-basic_1.0-9d0b67fed5b00f1dec364b2a4b5d0c5e7709050ed3cae84bf01cd4fe94b9b21b",
"dev-peer0.org2.example.com-basic_1.0-9d0b67fed5b00f1dec364b2a4b5d0c5e7709050ed3cae84bf01cd4fe94b9b21b"
]

        ips = ["172.19.0.26/16","172.19.0.28/16","172.19.0.24/16","172.19.0.23/16","172.19.0.27/16","172.19.0.25/16","172.19.0.22/16","172.19.0.21/16"]



    for i in range(0,NUM_ORG):
        # container_name = getCleanSubProcessOutput(cmd1_1 + str(i+1) + cmd1_2)

        print(containers_name[i])

        container_ID = getCleanSubProcessOutput(cmd2_1 + containers_name[i] + cmd2_2)
        print("container_ID " + container_ID)
        # container_IP = getCleanSubProcessOutput(cmd3_1 + containers_name[i] + cmd3_2)
        print("container_IP " + ips[i])
        veth_in_container = getCleanSubProcessOutput(cmd4_1 + containers_name[i] + cmd4_2)
        print("veth_in_container " + veth_in_container)
        veth_in_bridge = getCleanSubProcessOutput (cmd5_1 + str(veth_in_container) + cmd5_2)
        print("veth_in_bridge " + veth_in_bridge)

        for a in range(0,NUM_ORG):
            delaysVector.append(delaysMatrix[i][a])
            lowerBandwidthVector.append(lowerBandwidthMatrix[i][a])

        #print(container_name + " " + lowerBandwidthVector)


        containers.append(Container(container_ID, containers_name[i], veth_in_bridge, ips[i], delaysVector, int(upperbandwidht[upperbandwidhtIndex]), lowerBandwidthVector))
        upperbandwidhtIndex=upperbandwidhtIndex+1
        delaysVector=[]
        lowerBandwidthVector = []


    #for val in containers:
    #    a0 = os.popen("sudo docker exec "+ val.name +" apk update").read()
    #    a1 = os.popen("sudo docker exec "+ val.name +" apk upgrade").read()
    #    a2 = os.popen("sudo docker exec "+ val.name +" apk add iperf").read()
    #    print(val.toString())



        #a0 = subprocess.Popen(["sudo", "docker", "exec", val.name, "apk", "update"], shell=True, stderr=subprocess.STDOUT)
        #print(str(a0.communicate()[0])
        #a1 = subprocess.Popen(["sudo", "docker", "exec", val.name, "apk", "upgrade"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #print(str(a1.communicate()[0])
        #a2 = subprocess.Popen(["sudo", "docker", "exec", val.name, "apk", "add",  "iperf3"], shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        #print(str(a2.communicate()[0])


    delaysFile.close()
    containerBridgeInfoFile.close()
    return containers


def generateNetworkConf(containers, mode):
    print("")
    print("[FUNCTION] : generateNetworkConf() invoked... ", end = '')
    print(mode.upper() + " mode was chosen.")


###
    srcIndex = 0
    DEBUG_NETWORK=True
    for srcContainer in containers:
        #print(srcContainer.name + " network configuration... ", end = '')

        #temp = subprocess.Popen(["sudo", "tc", "qdisc", "del", "dev" , container.veth_in_bridge , "root"], stdout= subprocess.PIPE)
        #temp.communicate()

        if (mode == "cbq"):

            temp = subprocess.Popen(["sudo", "tc", "qdisc", "replace", "dev" , srcContainer.veth_in_bridge.replace(" ", "") , "root", "handle", "1:0", "cbq", "bandwidth", str(srcContainer.upperbandwidth) + "Mbit" ,  "avpkt","1000"], stdout= subprocess.PIPE)
            if DEBUG_NETWORK:
                print(temp.communicate()[0])
            else:
                temp.communicate()[0]

            temp = subprocess.Popen(["sudo",  "tc" , "class", "add", "dev",  srcContainer.veth_in_bridge.replace(" ", "") , "parent", "1:0", "classid", "1:1", "cbq", "bandwidth", str(srcContainer.upperbandwidth) + "Mbit",  "rate", str(srcContainer.upperbandwidth) + "Mbit", "allot", "1514", "avpk", "1000"], stdout= subprocess.PIPE)
            if DEBUG_NETWORK:
                print(temp.communicate()[0])
            else:
                temp.communicate()[0]


        elif(mode == "htb"):
            temp = subprocess.Popen(["sudo", "tc", "qdisc", "add", "dev" , srcContainer.veth_in_bridge.replace(" ", "") , "root", "handle", "1:0", "htb"], stdout= subprocess.PIPE)
            if DEBUG_NETWORK:
                print(temp.communicate()[0])
            else:
                temp.communicate()[0]

#,  "ceil", str(dstContainer.upperbandwidth) + "Mbit"]
	 #DA CAMBIARE PERCHE' SONO ENTRANTI
            temp = subprocess.Popen(["sudo",  "tc" , "class", "add", "dev",  srcContainer.veth_in_bridge.replace(" ", "") , "parent", "1:0", "classid", "1:1", "htb", "rate", str(srcContainer.upperbandwidth) + "Mbit"], stdout= subprocess.PIPE)
            if DEBUG_NETWORK:
                print(temp.communicate()[0])
            else:
                temp.communicate()[0]


        leaf_class = 2
        leaf_qdisc = 20
        dstIndex=0
        for dstContainer in containers:

            if(srcContainer.id != dstContainer.id):

                port = ((int(dstContainer.name.replace("peer0.org","").replace(".example.com","")) * 2 )+1) * 1000 + 51

                #print(dstContainer.name + " : " + str(port))
                if (mode == "cbq"):
                    temp = subprocess.Popen(["sudo",  "tc" , "class", "add", "dev" , srcContainer.veth_in_bridge.replace(" ", "") ,"parent" ,"1:1" ,"classid" ,"1:" +  str(leaf_class) , "cbq", "bandwidth", str(srcContainer.lowerBandwidth[dstIndex]) + "Mbit" , "rate", str(srcContainer.lowerBandwidth[dstIndex]) + "Mbit", "allot", "1514", "avpkt", "1000"], stdout= subprocess.PIPE)
                    if DEBUG_NETWORK:
                        print(temp.communicate()[0])
                    else:
                        temp.communicate()[0]
                elif(mode == "htb"):
                    #"ceil", str(container.lowerBandwidth[idx])  + "Mbit"
                    temp = subprocess.Popen(["sudo",  "tc" , "class", "add", "dev" , srcContainer.veth_in_bridge.replace(" ", "") ,"parent" ,"1:1" ,"classid" ,"1:" +  str(leaf_class) , "htb", "rate", str(srcContainer.lowerBandwidth[dstIndex]) + "Mbit", "ceil", str(srcContainer.lowerBandwidth[dstIndex])  + "Mbit"], stdout= subprocess.PIPE)
                    if DEBUG_NETWORK:
                        print(temp.communicate()[0])
                    else:
                        temp.communicate()[0]


                temp = subprocess.Popen(["sudo", "tc" , "filter", "replace", "dev", srcContainer.veth_in_bridge.replace(" ", ""), "parent", "1:0", "protocol", "ip", "u32", "match", "ip", "src", dstContainer.IP.replace('"', ""), "flowid", "1:" + str(leaf_class)], stdout= subprocess.PIPE)
                if DEBUG_NETWORK:
                    print(temp.communicate()[0])
                else:
                    temp.communicate()[0]

                #print("sudo tc qdisc replace dev" +  srcContainer.veth_in_bridge.replace(" ", "") + "parent 1:" + str(leaf_class) + "handle" + str(leaf_qdisc) + ": netem delay" + str(dstContainer.delays[srcIndex]).replace(" ", "") +"ms")

                temp = subprocess.Popen(["sudo",  "tc" , "qdisc", "replace", "dev" , srcContainer.veth_in_bridge.replace(" ", "") ,"parent" ,"1:" +str(leaf_class), "handle" , str(leaf_qdisc) + ":", "netem", "delay", str(dstContainer.delays[srcIndex]).replace(" ", "") +"ms"], stdout= subprocess.PIPE)
                if DEBUG_NETWORK:
                    print(temp.communicate()[0])
                else:
                    temp.communicate()[0]

                leaf_class+=1
                leaf_qdisc+=10
            dstIndex=dstIndex+1
        srcIndex += 1
    print("Completed!")

def checkDelaySymmetry(containers):
    i=0
    j=0
    wrong = 0
    for val in containers:
        for val2 in containers:
            if (containers[i].delays[j] != containers[j].delays[i]):
                #print("ERRORE! i: " + str(i+1) + "-> " + containers[i].delays[j] + " j: "+ str(j+1) + "-> " + containers[j].delays[i])
                wrong = 1
            j=j+1
        j=0
        i=i+1
    return wrong

def checkBandwidthSymmetry(containers):
    i=0
    j=0
    wrong = 0
    for val in containers:
        sum = 0
        for val2 in containers:
            sum =+ containers[i].lowerBandwidth[j]
            if (containers[i].lowerBandwidth[j] != containers[j].lowerBandwidth[i]):
                #print("ERRORE! i: " + str(i+1) + "-> " + containers[i].lowerBandwidth[j] + " j: "+ str(j+1) + "-> " + containers[j].lowerBandwidth[i])
                wrong = 1
            j=j+1
        j=0
        i=i+1
        if (sum > int(val.upperbandwidth)):
            print("ERROR: The sum of the bandwidth in " + val.name + " is bigger that the parent max value.")
        sum =0
    return wrong


########################################### UTILS FUNCTIONS ###################################################

def getCleanSubProcessOutput(cmd):
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = str(ps.communicate()[0])
    a = output.split("'")
    output = a[1]
    cleanedOutput= output[:len(output) - 2]
    return cleanedOutput

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def insertTransactionFunction(idAsset,threadStartTimes,threadFinishTimes):
    # print("index: " + str(idAsset))
    # print("len: " + str(len(threadStartTimes)))
    threadStartTimes[idAsset] = datetime.datetime.now()
    initTransaction = os.system('sudo ./peerTX.sh ' + str(ISSUER) + ' insert asset'+ str(idAsset) +' 1 1 1 '+ DONTSHOWOUTPUT )
    threadFinishTimes[idAsset] = datetime.datetime.now()


def poissonInsertTransactionFunction(idAsset):
    # print(str(idAsset)+"<------started")
    # print("len: " + str(len(threadStartTimes)))
    times = []
    times.append(datetime.datetime.now())
    initTransaction = os.system('sudo ./peerTX.sh ' + str(ISSUER) + ' insert asset'+ str(idAsset) +' 1 1 1 '+ DONTSHOWOUTPUT )
    times.append(datetime.datetime.now())
    # print(times)
    # print(str(idAsset)+"------>finished")
    return times

def deleteTransactionsFunction(R,seconds):
        for i in range(0,R*seconds):
            deleteTransaction = os.system('sudo ./peerTX.sh '+ str(ISSUER)+'  delete asset'+ str(i) + DONTSHOWOUTPUT)

def poissonProcess(mu, size):

        return poisson.rvs(mu=mu, size=size)

########################################### BOOT-UP FUNCTIONS ###################################################

class Container:
    def __init__(self, id, name, veth_in_bridge, IPwithSubnet,delaysVector,upperbandwidth,lowerBandwidth):
        self.id = id
        self.name = name
        self.veth_in_bridge = veth_in_bridge
        a = IPwithSubnet.split("/")
        finalIp = a[0] + '"'
        self.IP = finalIp
        self.delays = delaysVector
        self.upperbandwidth = upperbandwidth
        self.lowerBandwidth = lowerBandwidth

        #delays and lowerBandwidth are saved as
        # SRC DST1 DST2 .. DSTNUM_ORG

    def toString(self):
        #for i in self.delays:
            #print("i:" + i)
        bw = " lowerBandwidth: ["
        for val in self.lowerBandwidth:
            bw = bw + str(val) + ","
        bw = bw + "]"
        dl = " delays: ["
        for val in self.delays:
            dl = dl + str(val) + ","
        dl = dl + "]"

        return "[ "+ self.id + " : " + self.name + " : " + self.veth_in_bridge + " : " + self.IP + " : UPPERBW: " + str(self.upperbandwidth) + ":" + bw +  dl + "]"

    @staticmethod
    def saveConf(containers):
        f = open('data.pickle', 'wb')
        pickle.dump(containers, f)
        f.close()

    @staticmethod
    def loadConf():
        f = open('data.pickle', 'rb')
        unpickled_animals = pickle.load(f)
        f.close()
        #print(unpickled_animals)
        return unpickled_animals

########################################### BENCHMARKING FUNCTIONS ###################################################

def pingTestDelays(containers):
    print("[FUNCTION] : pingTestDelays() invoked... ")

    outputREPingFile = open(outputREPingFileName, 'w+')
    outputValuesPingFile = open(outputValuesPingFileName, 'w+')

    repetitionPing=5
    relativeErrorMatrix = np.zeros( (len(containers), len(containers)) )
    valuesMatrix = np.zeros( (len(containers), len(containers)) )
    a = datetime.datetime.now().replace(microsecond=0)

    j=0
    sumRelativeError = 0
    for container in containers:
        idx=0
        print(container.name)
        for val in containers:
            if(val.id != container.id):
                cmd = "sudo docker exec " + container.name + " ping -c " +  str(repetitionPing) + " -i "+ "0.1"+  " "  + val.name

                print(cmd)
                average = getCleanSubProcessOutput(cmd)
                #print(average)
                average = average.split("min/avg/max = ")[1].split("/")[1]
                #print("dim:" + str(len(a)))
                #print("average: " + average)
                #average = getCleanSubProcessOutput(cmd)
                #average = average.replace(" ms", "")
                average = float(average)
                expectedValue = float(container.delays[idx])*2

                #print(container.name + "->" + val.name + ": " + str(average))
                valuesMatrix[j][idx]  = average

                sumRelativeError += average

                if average < expectedValue:
                    relativeErrorMatrix[j][idx] =  ( (expectedValue - average)/ expectedValue) * 100
                else:
                    relativeErrorMatrix[j][idx] =  ( (average - expectedValue)/ expectedValue) * 100

                    #print ("[DELAY ERROR] : [" + container.name + " -> " + val.name + "]"+ "  time received: "+ str(average)+ ". expected [" + str(minLatencyValue) + "," + str(maxLatencyValue) + "]")
                    #print ("to be a right value the tolerance should have been " +  str(additionalToleranceNeeded) + "% higher.")

            idx+=1
        j=j+1




    b = datetime.datetime.now().replace(microsecond=0)
    print("TIME USED: " + str(b-a))

    print("[FUNCTION] : pingTestDelays() has finished. ")

    print("")

    print("[ -----    REPORT    ----- ]")

    averageRelativeError=sumRelativeError/56

    print("Average relative error: " + str(averageRelativeError))
    #print("Guessed with tolerance " + str(tolerance) + " : " + str(guessed))
    #print("The wrong ones are " + str(wrong) + ".")
    #print("The delay values were in average distant " + str(averagePercentualDistance) + "% distant from the expected value.")
    i=0
    for val1 in containers:
        j=0
        print(val1.name  + " ", end = "", file = outputREPingFile )
        print(val1.name  + " ", end = "", file = outputValuesPingFile )


        for val2 in containers:
            print("{:.2f}".format(relativeErrorMatrix[i][j]) + " ", end = "", file = outputREPingFile )
            print("{:.2f}".format(valuesMatrix[i][j]) + " ", end = "", file = outputValuesPingFile )

            j=j+1
        print("", file = outputREPingFile)
        print("", file = outputValuesPingFile)

        i = i +1
    print("DONE!")

def iperfTest(containers):

  def server(clientname):
          print("[ Server: " + clientname + " ]")
          a = os.popen("sudo docker exec "+ clientname+" iperf -s -P 7").read()
          print("[ Iperf Server "+ clientname + " closed]")

  def client(clientname, servername):
          #print("")
          #print("dentro il client di nome:" + clientname)
          a = os.popen("sudo docker exec "+ clientname + " iperf -c " + servername + " -t 60").read()
          return a

  y=[]
  relativeErrorMatrix = np.zeros( (len(containers), len(containers)) )
  valuesMatrix = np.zeros( (len(containers), len(containers)) )
  relativeErrorIperfFile = open(relativeErrorIperfFileName, 'w+')
  bandwidthValuesFile = open(bandwidthValuesFileName, 'w+')
  retry=0


  j=0
  for container in containers:
      if (retry >= MAX_RETRY_TIME):
          print("ABORTING IPERFTEST : [ERROR]: CLIENTS ARE NOT RESPONDING. ")
          break
      x = threading.Thread(target=server, args=(container.name,))
      x.start()
      y.append(x)
      done= np.zeros(NUM_ORG)
      i=0
      count = 0

      with concurrent.futures.ThreadPoolExecutor() as executor:
          while count<NUM_ORG-1: #I WAIT UNTIL ALL THE OTHER CLIENTS HAVE DONE THE IPERF TEST
                if(container.name != containers[i].name and done[i]!=1):
                    future = executor.submit(client, containers[i].name, container.name)
                    return_value = future.result()
                    if (len (return_value.split("\n")) > 7):
                        print(return_value)
                        expectedValue = container.lowerBandwidth[i]
                        #var = return_value.split("\n")[6].split(" ")[10]
                        #g =0
                        #for p in return_value.split("\n")[6].split(" "):
                        #    print(str(g) + ": " + p)
                        #    g+=1

                        var = return_value.split("MBytes")[1].replace("Mbits/sec", "").replace(" ","").replace("\n","")
                        print("[" +  containers[i].name +" : " + var + "]")
                        var = float(var)
                        valuesMatrix[i][j] = float(var)
                        if var < expectedValue:
                                relativeErrorMatrix[i][j] =  ( (expectedValue - var)/ expectedValue) * 100
                        else:
                                relativeErrorMatrix[i][j] =  ( (var - expectedValue)/ expectedValue) * 100
                        count+=1
                        done[i]=1

                        #print("relativeErrorMatrix")
                        #for a in range(0,NUM_ORG):
                        #    for b in range (0,NUM_ORG):
                        #        print(str(relativeErrorMatrix[a][b]) + " ", end ="")
                        #    print("")

                if ((i+1)%(NUM_ORG) < i):
                    retry= retry+1
                    print("[WARNING] : Some of the clients are not responding. I'll retry.")
                i = (i+1)%(NUM_ORG)
                if count == NUM_ORG-1:
                    print("[SUCCESS] : All clients has been measured by " + container.name)
                if (retry >=3):
                    count = NUM_ORG
                    relativeErrorMatrix[i][j] =  -1


      j=j+1
      retry = 0

      ####SECOND RETRY



  i = 0
  j=0
  for val1 in containers:
      j=0
      for val2 in containers:
        print("{:.2f}".format(relativeErrorMatrix[i][j]) + " ", end = "", file = relativeErrorIperfFile )
        print("{:.2f}".format(valuesMatrix[i][j]) + " ", end = "", file = bandwidthValuesFile )
        j=j+1

      print("", file = relativeErrorIperfFile)
      print("", file = bandwidthValuesFile)
      i=i+1

def measureEndorsingTime(mode):
      # ct stores current time
      print("[FUNCTION] : measureEndorsingTime() invoked... ")

      ct = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
      endorsingTimes=[]

      initTransaction = os.system('sudo ./peerTX.sh 1 init 1>/dev/null')

      for i in range(0,NUM_ORG):
          #print("peer number " + str(i+1) )

          cmd = "docker logs --since " + str(ct) + " peer0.org" + str(i+1) + ".example.com"
          a = getCleanSubProcessOutput(cmd)


          if "grpc.service=protos.Endorser grpc.method=ProcessProposal" in a:
              result = str(a).split("grpc.call_duration=")[1].split("\\n")[0]
              endorsingTimes.append(float(result.replace("ms", "").replace("ns", "").replace("s","")))
              print("peer0.org" +str(i+1)+ ".example.com responded in " + result)
          else:
              print("No endorsment from peer" + str(i+1))

      if mode == "ONEMAXTIME":
          max = endorsingTimes[0]
          index = 0
          i = 1
          for value in endorsingTimes:
               if value> max:
                   max = value
                   index = i
               i+=1


          print("")
          print("The endorser is peer" + str(index)+".")
          print("The endorsing time is " + str(max) + "ms")
          print("")

      if mode == "ONEMINTIME":
          min = endorsingTimes[0]
          index = 0
          i = 1
          for value in endorsingTimes:
               if value< min:
                   min = value
                   index = i
               i+=1

          print("")
          print("The endorser is peer" + str(index)+".")
          print("The endorsing time is " + str(min) + "ms")
          print("")

        # return "{setRate: "+str(R)+ ", actualRate: " + str(experimentalR_tillJoining) + ", average: " + str(average) +"}"

def measureCPUoccupation():
    return psutil.cpu_percent()

def measureRAMoccupation():
    return psutil.virtual_memory()[2]
    # log = str(ps.communicate()[0].split("%Cpu(s): ")[1].split(" us,")[0])
    # print("CPU UTILIZATION: " + log)


class Measuration:
    def __init__(self, setRate, offeredLoad ,throughput, average, CPUoccupation,  RAMoccupation):
        self.setRate = round(float(setRate),1)
        self.offeredLoad = round(float(offeredLoad),1)
        self.throughput = round(float(throughput),1)
        self.average = round(float(average),1)
        self.CPUoccupation = round(float(CPUoccupation),1)
        self.RAMoccupation = round(float(RAMoccupation),1)

    def toString(self):
         return "[setRate:" + str(self.setRate) + "; offeredLoad: " + str(self.offeredLoad) + "; throughput: " + str(self.throughput) + "; average: "+ str(self.average) + "; CPUoccupation: "+ str(self.CPUoccupation) + "; RAMoccupation: "+ str(self.RAMoccupation) + "]\n"
    def toStructure(self):
         return "[" + str(self.setRate) + "; " + str(self.offeredLoad) + "; " + str(self.throughput) + "; "+ str(self.average) + "; "+ str(self.CPUoccupation) + "; "+ str(self.RAMoccupation) + "]\n"

def generate_offeredLoad_throughput_graph(measurations):
    col=["b","k","r","g","m","brown","c","tan","grey","y","lime","orange"]
    max0=3.000
    max1=6.000
    type = "Poisson"

    TINY_SIZE = 10
    SMALL_SIZE = 12
    MEDIUM_SIZE = 14
    BIGGER_SIZE = 16
    plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=MEDIUM_SIZE)     # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    # OPEN_0=[248.0 ,254.0 ,263.0 ,275.0 ,291.0 ,310.0 ,334.0 ,360.0 ,393.0 ,433.0 ,921.0 ,374959.0 ,65474312.0 ,109543628.0 ,140868911.0 ,164618651.0 ,197696417.0 ,219366605.0 ,235311825.0]
    # RND4_0=[267.0 ,284.0 ,303.0 ,326.0 ,350.0 ,378.0 ,411.0 ,451.0 ,494.0 ,548.0 ,1158.0 ,223695.0 ,65615799.0 ,110067871.0 ,141183496.0 ,164613740.0 ,197455348.0 ,219623643.0 ,235112982.0]
    # RNDk_0=[150.0 ,182.0 ,225.0 ,284.0 ,327.0 ,362.0 ,405.0 ,451.0 ,494.0 ,548.0] #prac(cut decimal)
    # DSLM_0=[996.0 ,1002.0 ,1002.0 ,1001.0 ,1000.0 ,1000.0 ,1000.0 ,1000.0 ,999.0 ,1000.0] # their approach
    # OOD4_0=[127.0 ,130.0 ,132.0 ,135.0 ,138.0 ,141.0 ,144.0 ,147.0 ,151.0]#??? REPEAT


    plt.figure()
    plt.grid()

    print(list(map(lambda n: n.offeredLoad,measurations)))
    plt.axline([0, 0], [1, 1], color=col[2])

    plt.plot(list(map(lambda n: n.setRate,measurations)),list(map(lambda n: n.offeredLoad,measurations)),'--',linewidth=2 , color=col[1], label='Offered Load[tx/s]' )

    # plt.plot(list(map(lambda n: n.setRate,measurations)),list(map(lambda n: n.throughput,measurations)),'--',linewidth=2 , color=col[2], label="Throughput[tx/s]" )
    a= 8

    plt.xlabel('Set Rate [tx/s]')
    plt.ylim(ymin=0, ymax=a)
    plt.ylabel('Offered Load [tx/s]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("SetRate-OfferedLoad_8org"+type + ".pdf", bbox_inches='tight')
    # plt.savefig("zero-Gamma(10-90)t", bbox_inches='tight')
    # plt.show()
    plt.clf()

    plt.figure()
    plt.grid()


    # plt.plot(list(map(lambda n: n.setRate,measurations)),list(map(lambda n: n.offeredLoad,measurations)),'--',linewidth=2 , color=col[1], label=r'Offered Load[tx/s]' )

    measurations = sorted(measurations, key=lambda x: x.offeredLoad)

    plt.axline([0, 0], [1, 1], color=col[2])

    plt.plot(list(map(lambda n: n.offeredLoad,measurations)),list(map(lambda n: n.throughput,measurations)),'--',linewidth=2 , color=col[1], label="Throughput[tx/s]" )


    plt.xlabel('Offered Load [tx/s]')
    plt.ylim(ymin=0, ymax=a)
    plt.ylabel('Throughput Load [tx/s]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("OfferedLoad-Throughput_8org_"+type+".pdf", bbox_inches='tight')
    # plt.savefig("zero-Gamma(10-90)t", bbox_inches='tight')
    # plt.show()
    plt.clf()


    plt.plot(list(map(lambda n: n.offeredLoad,measurations)),list(map(lambda n: n.CPUoccupation,measurations)),'--',linewidth=2 , color=col[1], label="CPU consumption [%]" )
    plt.plot(list(map(lambda n: n.offeredLoad,measurations)),list(map(lambda n: n.RAMoccupation,measurations)),'--',linewidth=2 , color=col[2], label="RAM consumption [%]" )


    plt.xlabel('Offered Load [tx/s]')
    plt.ylim(ymin=0, ymax=a)
    plt.ylabel('Occupation [%]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("OfferedLoad-Occupation_8org"+type + ".pdf", bbox_inches='tight')
    # plt.savefig("zero-Gamma(10-90)t", bbox_inches='tight')
    # plt.show()
    plt.clf()
    maxAverage = max(list(map(lambda n: n.average,measurations)))

    # plt.axline([0, 0], [8, maxAverage*1.1], color=col[2])

    plt.plot(list(map(lambda n: n.offeredLoad,measurations)),list(map(lambda n: n.average,measurations)),'--',linewidth=2 , color=col[1], label="Average Endorsement execution Time [ms]" )

    plt.xlabel('Offered Load [tx/s]')
    plt.ylim(ymin=0, ymax=maxAverage*1.1)
    plt.ylabel('Average Endorsement execution Time [ms]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("OfferedLoad-AEET_8org"+type + ".pdf", bbox_inches='tight')
    # plt.savefig("zero-Gamma(10-90)t", bbox_inches='tight')
    # plt.show()
    plt.clf()

def measure_stat_uniform(R,seconds):

        print("[FUNCTION] : measureServiceStats() invoked... ")

        PRE_JOIN_THREADS = True

        Actualtimestamp = timestamp()
        # folderName = Actualtimestamp + "_R="+str(R)  + "_seconds=" + str(seconds)
        #
        #
        # cmd = "mkdir serviceStatsOutput/" + folderName

        # createFolderCommand = getCleanSubProcessOutput(cmd)


        y=[]
        executionDurations=[]
        periodDurations=[]
        committedBlocks=[]
        responses =[]

        totalDuration = 0
        totalElapsingTime = 0
        preJoined = 0
        afterJoined = 0
        #
        threadStartTimes= [None] * (R*seconds)

        threadFinishTimes=[None] * (R*seconds)

        startExperiment = datetime.datetime.now()
        print("Starting the experiment - Timestamp: " + str(startExperiment))

        CPUoccupation = []
        RAMoccupation = []

        for a in range(0, R*seconds):
                 start  = datetime.datetime.now()
                 if THREADS:
                    x = threading.Thread(target=insertTransactionFunction, args=(a,threadStartTimes,threadFinishTimes))
                    x.start()
                    if (a == R*seconds - 1):
                         finishSpawningTime = datetime.datetime.now()
                    CPUoccupation.append(float(measureCPUoccupation()))
                    RAMoccupation.append(float(measureRAMoccupation()))

                    y.append(x)
                    if PRE_JOIN_THREADS:
                        interval = R
                        if (a%interval == 0 and a > 2* interval):
                            for i in range(a-2*interval, a-interval, 1):
                                if not y[i].is_alive():
                                    y[i].join()
                                    preJoined = preJoined + 1

                 else:
                    insertTransactionFunction(a)



                 timeExecution = (datetime.datetime.now()-start).total_seconds()
                 remaining = 1/R - timeExecution
                 if remaining > 0:
                    time.sleep(remaining)

                 timePeriod = (datetime.datetime.now()-start).total_seconds()
                 executionDurations.append(timeExecution)
                 periodDurations.append(timePeriod)

        offeredLoad = ((R*seconds)/(finishSpawningTime - startExperiment).total_seconds())

        if THREADS:
            print("All the thread have been deployed - Timestamp: " + timestamp())

            print("Joining thread....", end="")

            for a in range(0,len(y)):
                if not y[a].is_alive():
                    y[a].join()
                    afterJoined = afterJoined + 1

            print("...finished!")

            print("Prejoined: " + str(preJoined) +  " afterJoined: " + str(afterJoined))

        # throughput = ((R*seconds)/(datetime.datetime.now() - startExperiment).total_seconds())

        # print("The first thread has started at " + str(threadStartTimes[len(threadStartTimes)-1]))
        #
        # print("The last thread finished at" + str(threadFinishTimes[len(threadStartTimes)-1]))

        # print("Experimentally R is:")
        # print("offeredLoad:" + str(offeredLoad))
        # print("Throughput:" + str(throughput))

        # timebinsperiod = range(0, len(periodDurations), 1)
        # timebinsexecution = range(0, len(executionDurations), 1)


        # #plt.plot( timebins, executionDurations)
        # plt.plot( timebinsperiod, periodDurations)
        # plt.xlabel("TX number")
        # plt.ylabel("Seconds")
        # plt.savefig("serviceStatsOutput/"+folderName+"/periodtime.jpeg")
        # plt.clf()
        #
        # plt.plot( timebinsexecution, executionDurations)
        # plt.xlabel("TX number")
        # plt.ylabel("Seconds")
        # plt.savefig("serviceStatsOutput/"+folderName+"/executiontime.jpeg")
        # plt.clf()
        logs = []

        #IF NUMBER OF REQUESTS DECRESES THIS IS THE PROBLEM
        time.sleep(2)

        totalAverage = 0
        sum = 0

        for i in range(1,NUM_ORG+1):
             cmd2 = "docker logs --since " + str(Actualtimestamp) + " peer0.org" + str(i) + ".example.com"
             ps = subprocess.Popen(cmd2,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
             log = str(ps.communicate()[0])
             logs.append(log)

        if THREADS:
                x = threading.Thread(target=deleteTransactionsFunction, args=[R,seconds, ])
                x.start()

        for i in range(1,NUM_ORG+1):

             list = logs[i-1].split("grpc.service=protos.Endorser grpc.method=ProcessProposal")
             j = 0
             for value in list:
                 if (j != 0):
                         responses.append(float(value.split("grpc.call_duration=")[1].split("ms")[0].split("s\\n")[0].split(" ")[0]))
                 j =j+1


             list2 = logs[i-1].split("Committed block [")
             j = 0
             for value in list2:
                    if (j != 0):
                         committedBlocks.append(value.split("]")[0])
                    j =j+1

             #print("PEER0.ORG" + str(i) + ".EXAMPLE.COM RESPONSES:" + str(len(responses)) + " Committed Blocks: " + str(len(committedBlocks)), file=numberOfResponses)

             for u in responses:
                sum= sum + u
             average = sum/(len(responses))
             # print(average)

             totalAverage = totalAverage + average



             count = 0
             for q in range(0, (R*seconds)-len(responses)):
                 responses.append(-1)
                 count = count +1
                 #print("AGGIUNTO")

             if count > 0 :
                 print("[WARNING] : Peer0.org " + str(i) +" non ha risposto ad "+ str(count) +" richieste")

             sum = 0

            #  bins = range(-1,500, 1)
            #  pltBins = range(0, len(responses), 1)
            #  arr = plt.hist(responses, 20 , histtype="barstacked")
            #  plt.title("peer0.org"+str(i)+".example.com")
            #  plt.xlabel("Service Time [ms]", fontsize = 7)
            #  plt.ylabel("Count", fontsize = 7)
            #  plt.figtext(.7, .8, "Avg = " +str("{:.2f}".format(average)) + "ms")
            #  plt.savefig("serviceStatsOutput/"+folderName+"/org"+str(i)+"hist.jpeg")
            #  plt.clf()
            #
            #  bins = range(0,50, 1)
            #  arr = plt.hist(responses, bins , histtype="barstacked")
            #  plt.title("peer0.org"+str(i)+".example.com")
            #  plt.xlabel("Service Time [ms]", fontsize = 7)
            #  plt.ylabel("Count", fontsize = 7)
            #  plt.savefig("serviceStatsOutput/"+folderName+"/org"+str(i)+"hist_noOutliers.jpeg")
            #  plt.clf()
            #  #media_mobile = []
            #  #media_mobile = moving_average(responses,int(R))
            #  #last = media_mobile[len(media_mobile)-1]
            #  #for i in range(0,len(responses) - len(media_mobile)):
            # #      media_mobile = np.append(media_mobile,[last])
            #  #plt.plot( pltBins, responses, pltBins, media_mobile)
            #
            #  plt.plot( pltBins, responses)
            #  plt.title("peer0.org"+str(i)+".example.com")
            #  plt.xlabel("Tx Number", fontsize = 7)
            #  plt.ylabel("Service Time [ms]", fontsize = 7)
            #  plt.savefig("serviceStatsOutput/"+folderName+"/org"+str(i)+"plot.jpeg")
            #  plt.clf()
            #  responses.clear()
            #  committedBlocks.clear()
            #  plt.clf()

        sum = 0
        for value in CPUoccupation:
                 sum = sum + value

        averageCPUoccupation = sum/len(CPUoccupation)

        sum = 0
        for value in RAMoccupation:
                 sum = sum + value

        averageRAMoccupation = sum/len(RAMoccupation)

        firstStart = min(threadStartTimes)
        lastFinish = max(threadFinishTimes)

        throughput = (R*seconds) / ((lastFinish - firstStart).total_seconds())
        print("real throughput: "+ str(throughput))

        print("CPU AVERAGE: " + str(averageCPUoccupation))
        print("RAM AVERAGE: " + str(averageRAMoccupation))

        # print("startTime")
        # for value in threadStartTimes:
        #      print(str(value))
        #
        # print("min start time" + str(min(threadStartTimes)))
        #
        # print("endTime")
        # for value in threadFinishTimes:
        #      print(str(value))
        #
        # print("max end time" + str(max(threadFinishTimes)))

        # print("Finished calculating images!" )

        #print("Finished. The output is in "+ folderName +" folder.")

        print("Cleaning Environment ...", end="" )

        if THREADS:
             x.join()
        else:
             deleteTransactionsFunction(R,id)

        print("....done." )

        return Measuration(R,offeredLoad,throughput,totalAverage/NUM_ORG, averageCPUoccupation, averageRAMoccupation)


def measure_stat_poisson(R,seconds):
         print("[FUNCTION] : measureServiceStats() invoked... ")

         y=[]
         executionDurations=[]
         periodDurations=[]
         committedBlocks=[]
         responses =[]

         totalDuration = 0
         totalElapsingTime = 0
         preJoined = 0
         afterJoined = 0
         timestamps = []



         Actualtimestamp = timestamp()
         # folderName = Actualtimestamp + "_R="+str(R)  + "_seconds=" + str(seconds)
         #
         # cmd = "mkdir serviceStatsOutput/" + folderName

         # createFolderCommand = getCleanSubProcessOutput(cmd)

        ### START EXPERIMENT


         totalTransactions = 0
         threadStartTimes = []
         threadFinishTimes = []
         transactionDistribution = poissonProcess(R,seconds)
         for value in transactionDistribution:
             totalTransactions = totalTransactions+value
         # for i in range(0,totalTransactions):
         #    threadStartTimes.append(None)
         #    threadFinishTimes.append(None)


         print("totalTransactions: "+ str(totalTransactions))
         # threadStartTimes = [None]*(totalTransactions)
         # threadFinishTimes = [None]*(totalTransactions)

         print("len:" + str(len(threadStartTimes)))
             # print(str(value), end=" ")
         # poissonBins = range(0, len(transactionDistribution), 1)
         # plt.bar(poissonBins, transactionDistribution, width=1, edgecolor="black", linewidth=0.5)
         # plt.xlabel("Second")
         # plt.ylabel("Number of TXs")
         # plt.savefig("serviceStatsOutput/"+folderName+"/txDistribution.jpeg")
         # plt.clf()

         txId=0
         max_workers = max(transactionDistribution)

         startExperiment = datetime.datetime.now()

         CPUoccupation = []
         RAMoccupation = []
         results = []
         if max_workers > 0:
             with ThreadPoolExecutor(max_workers=max(transactionDistribution)) as executor:
                 for second in range(0,seconds):
                     startPeriod  = datetime.datetime.now()


                     times = transactionDistribution[second]
                     # res = executor.map(insertTransactionFunction,range(txId,txId+times),threadStartTimes,threadFinishTimes)

                     # res = executor.map(poissonInsertTransactionFunction,range(txId,txId+times))
                     if (second == seconds-1):
                                print("finished spawning")
                                finishSpawningTime = datetime.datetime.now()
                     for result in executor.map(poissonInsertTransactionFunction,range(txId,txId+times)):
	                        results.append(result)
                     # results.append(res)


                     CPUoccupation.append(float(measureCPUoccupation()))
                     RAMoccupation.append(float(measureRAMoccupation()))
                     txId = txId + times
                     #totalTransactions = totalTransactions + times
                     # for value in res:
                     #     timestamps.append(str(value))

                     timeExecution = (datetime.datetime.now()-startPeriod).total_seconds()

                     if len(periodDurations) > 0 :
                         if periodDurations[-1] - 1 > 0:
                            remaining = 1 - timeExecution - (periodDurations[len(periodDurations)-1] - 1)
                         else:
                            remaining = 1 - timeExecution
                     else:
                         remaining = 1 - timeExecution

                     #print("sleeping " + str(remaining))

                     if remaining > 0:
                         #print(str(times) + " sleeping " + str(remaining))
                         time.sleep(remaining)
                     #else:
                    #     print("not sleeping - " + str(times) + " - " + str(timeExecution) )
                     executionDurations.append(timeExecution)
                     timePeriod = (datetime.datetime.now()-startPeriod).total_seconds()
                     periodDurations.append(timePeriod)
         else:
                print("Tutti zero!")

        # print(threadStartTimes)

         for value in results:
            threadStartTimes.append(value[0])
            threadFinishTimes.append(value[1])

         # results = [r.result() for r in results[0]]
         # print(threadStartTimes)
         # print(threadFinishTimes)

         # throughput = (totalTransactions/((datetime.datetime.now() - startExperiment).total_seconds()))

         offeredLoad = (totalTransactions/((finishSpawningTime - startExperiment).total_seconds()))

         print("offeredLoad = " + str(offeredLoad))

         print("The first thread has started at " + str(min(threadStartTimes)))

         print("The last thread finished at" + str(max(threadFinishTimes)))

         # print("After having joined all the threads. R: " + str(throughput))


         executor.shutdown(True)

         #for value in timestamps:
             #print(str(value))


         #print(times)

         if THREADS:
            x = threading.Thread(target=deleteTransactionsFunction, args=[R,seconds, ])
            x.start()

         timebinsperiod = range(0, len(periodDurations), 1)
         timebinsexecution = range(0, len(executionDurations), 1)


        #plt.plot( timebins, executionDurations)
        #  plt.plot( timebinsperiod, periodDurations)
        #  plt.xlabel("TX number")
        #  plt.ylabel("Seconds")
        #  plt.savefig("serviceStatsOutput/"+folderName+"/periodtime.jpeg")
        #  plt.clf()
        #
        #  plt.plot( timebinsexecution, executionDurations)
        #  plt.xlabel("TX number")
        #  plt.ylabel("Seconds")
        #  plt.savefig("serviceStatsOutput/"+folderName+"/executiontime.jpeg")
        #  plt.clf()
        #
        #  TXseconds=[]
        #  for value in timestamps:
        #      TXseconds.append((datetime.datetime.strptime(str(value), "%Y-%m-%dT%H:%M:%S") - startExperiment).total_seconds())
        #
        #  #for value in TXseconds:
        # #     print(value)
        #
        #  arr = plt.hist(TXseconds, seconds , histtype="barstacked")
        #  plt.xlabel("Time", fontsize = 7)
        #  plt.ylabel("Count", fontsize = 7)
        #  plt.savefig("serviceStatsOutput/"+folderName+"/timeInsertion.jpeg")
        #  plt.clf()


         logs = []
         totalAverage = 0

         for i in range(1,NUM_ORG+1):
              cmd2 = "docker logs --since " + str(Actualtimestamp) + " peer0.org" + str(i) + ".example.com"
              ps = subprocess.Popen(cmd2,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
              log = str(ps.communicate()[0])
              # print(log)
              logs.append(log)

                 #x = threading.Thread(target=deleteTransactionsFunction, args=[R,seconds, ])
                 #x.start()



         for i in range(1,NUM_ORG+1):

              list = logs[i-1].split("grpc.service=protos.Endorser grpc.method=ProcessProposal")
              j = 0
              for value in list:
                  if (j != 0):
                          #print("response:")
                          #print(float(value.split("grpc.call_duration=")[1].split("ms")[0].split("s\\n")[0]))
                          responses.append(float(value.split("grpc.call_duration=")[1].split("ms")[0].split("s\\n")[0].split(" ")[0]))
                  j =j+1


              list2 = logs[i-1].split("Committed block [")
              j = 0
              for value in list2:
                     if (j != 0):
                          committedBlocks.append(value.split("]")[0])
                     j =j+1


              sum = 0
              for u in responses:
                 sum= sum + u
              average = sum/(R*seconds)

              totalAverage = totalAverage + average


             #  bins = range(-1,500, 1)
             #  pltBins = range(0, len(responses), 1)
             #  arr = plt.hist(responses, 20 , histtype="barstacked")
             #  plt.title("peer0.org"+str(i)+".example.com")
             #  plt.xlabel("Service Time [ms]", fontsize = 7)
             #  plt.ylabel("Count", fontsize = 7)
             #  plt.figtext(.7, .8, "Avg = " +str("{:.2f}".format(average)) + "ms")
             #  plt.savefig("serviceStatsOutput/"+folderName+"/org"+str(i)+"hist.jpeg")
             #  plt.clf()
             #
             #  bins = range(0,50, 1)
             #  arr = plt.hist(responses, bins , histtype="barstacked")
             #  plt.title("peer0.org"+str(i)+".example.com")
             #  plt.xlabel("Service Time [ms]", fontsize = 7)
             #  plt.ylabel("Count", fontsize = 7)
             #  plt.savefig("serviceStatsOutput/"+folderName+"/org"+str(i)+"hist_noOutliers.jpeg")
             #  plt.clf()
             #  #media_mobile = []
             #  #media_mobile = moving_average(responses,int(R))
             #  #last = media_mobile[len(media_mobile)-1]
             #  #for i in range(0,len(responses) - len(media_mobile)):
             # #      media_mobile = np.append(media_mobile,[last])
             #  #plt.plot( pltBins, responses, pltBins, media_mobile)
             #
             #  plt.plot( pltBins, responses)
             #  plt.title("peer0.org"+str(i)+".example.com")
             #  plt.xlabel("Tx Number", fontsize = 7)
             #  plt.ylabel("Service Time [ms]", fontsize = 7)
             #  plt.savefig("serviceStatsOutput/"+folderName+"/org"+str(i)+"plot.jpeg")
             #  plt.clf()
              responses.clear()
              committedBlocks.clear()
              plt.clf()

         sum = 0
         for value in CPUoccupation:
             sum = sum + value

         averageCPUoccupation = sum/len(CPUoccupation)

         sum = 0
         for value in RAMoccupation:
             sum = sum + value

         averageRAMoccupation = sum/len(RAMoccupation)

         print("CPU AVERAGE: " + str(averageCPUoccupation))
         print("RAM AVERAGE: " + str(averageRAMoccupation))

         firstStart = min(threadStartTimes)
         lastFinish = max(threadFinishTimes)

         throughput = (totalTransactions) / ((lastFinish - firstStart).total_seconds())
         print("throughput = " + str(throughput))

         # print("startTime")
         # for value in threadStartTimes:
         #     print(str(value))
         #
         # print("endTime")
         # for value in threadFinishTimes:
         #     print(str(value))

         print("Finished calculating images!" )

         # print("Finished. The output is in "+ folderName +" folder.")

         print("Cleaning Environment ...", end="" )


         # with ThreadPoolExecutor(max_workers=max(transactionDistribution)) as executor:
         #             executor.map(deleteTransactionsFunction,R, seconds)

         print("....done." )
         #---->ACTUALRATE DIPENDE DA TXID VEDERE IL SUO VALORE DOPO TUTTO IL LOOP
         #PER AVERAGE CONTROLLA I PROCESSPROPOSAL CHE CI SONO NEI LOG. LA MEDIA 'E SEMPRE ZERO PERO'
         return Measuration(R,offeredLoad,throughput,totalAverage/NUM_ORG, averageCPUoccupation, averageRAMoccupation)
