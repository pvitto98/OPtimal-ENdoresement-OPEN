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
from OLDconfiguration import *
from operator import attrgetter
import statistics





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
NUM_ERROR = 0

ISSUER=1

DONTSHOWOUTPUT = '> /dev/null 2>&1'
baseName='client'






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

def insertTransactionFunction(idAsset,threadStartTimes,threadFinishTimes, R,SELECTION_ALGORITHM,N,CPU):
    # print("index: " + str(idAsset))
    # print("len: " + str(len(threadStartTimes)))
    threadStartTimes[idAsset] = datetime.datetime.now()
    #print(threadStartTimes[idAsset])
    #print(SELECTION_ALGORITHM)
    initTransaction = os.system('sudo ./peerTX.sh ' + str(ISSUER) + ' insert assetqss'+ "_"+str(R)+ "_" +str(CPU) + "_"+ str(idAsset) +' 1 1 1 1 ' + SELECTION_ALGORITHM +" " +  N  + " "+ DONTSHOWOUTPUT)
    if initTransaction!=0:
        #NUM_ERROR = NUM_ERROR + 1
        print("[ERROR]: asset"+str(R)+ "_" +str(CPU) + "_"+ str(idAsset)+  " WAS NOT ADDED TO THE LEDGER.")
    threadFinishTimes[idAsset] = datetime.datetime.now()

def deleteTransactionsFunction(R,seconds):
        for i in range(0,R*seconds):
            deleteTransaction = os.system('sudo ./peerTX.sh '+ str(ISSUER)+'  delete asset'+ str(i) + DONTSHOWOUTPUT)

def limitCPU(val):
    initTransaction = os.system('./setCPUlimit.sh ' + str(val))



########################################### BENCHMARKING FUNCTIONS ###################################################


def measureCPUoccupation():
    return psutil.cpu_percent()


class Measuration:
    def __init__(self, setRate, offeredLoad ,throughput, average, CPUoccupation,  RAMoccupation, logs=[], threadStartTimes=[],endorsementTime=0):
        self.setRate = round(float(setRate),1)
        self.offeredLoad = round(float(offeredLoad),4)
        self.throughput = round(float(throughput),1)
        self.average = round(float(average),1)
        self.CPUoccupation = round(float(CPUoccupation),1)
        self.RAMoccupation = round(float(RAMoccupation),1)
        self.logs=logs
        self.threadStartTimes=threadStartTimes
        self.endorsementTime=endorsementTime

    def toString(self):
         return "[setRate:" + str(self.setRate) + "; offeredLoad: " + str(self.offeredLoad) + "; throughput: " + str(self.throughput) + "; average: "+ str(self.average) + "; CPUoccupation: "+ str(self.CPUoccupation) + "; RAMoccupation: "+ str(self.RAMoccupation) + "; EndorsementTime: "+str(self.endorsementTime) + "]\n"
    def toStructure(self):
         return "[" + str(self.setRate) + ";" + str(self.offeredLoad) + ";" + str(self.throughput) + ";"+ str(self.average) + ";"+ str(self.CPUoccupation) + ";"+ str(self.RAMoccupation) + ";"+ str(self.endorsementTime)+"]\n"

def toFile(vector,label):
    result=""
    if (label!=""):
        result=label+ ": "
    result=result+"["
    for i in range(0,len(vector)):
        result =result+str(vector[i])
        if i!=len(vector)-1:
            result =result+";"
    result =result+"]\n"
    return result

def ydimGraph(yvector,error):
    maxY=max(yvector)
    errorForGraph=-1
    for i in range(0,len(yvector)):
        if yvector[i]==maxY:
            errorForGraph=error[i]
            break
    return (maxY + errorForGraph)*1.1

def cm_to_inch(value):
    return value/2.54

def measure_stat_uniform(R,seconds,SELECTION_ALGORITHM,N,TRY,folderName=""):

        print("[FUNCTION] : measureServiceStats() invoked... ")

        PRE_JOIN_THREADS = True

        NUM_ERROR = 0

        Actualtimestamp = timestamp()

        y=[]
        executionDurations=[]
        periodDurations=[]
        committedBlocks=[]
        txIDs=[]
        delays=[]
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

############################################################### THREAD GENERATION
        CPUoccupation = []
        RAMoccupation = []

        for a in range(0, R*seconds):
                 start  = datetime.datetime.now()
                 if THREADS:
                    x = threading.Thread(target=insertTransactionFunction, args=(a,threadStartTimes,threadFinishTimes,R,SELECTION_ALGORITHM,N,TRY))
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
                    insertTransactionFunction(a,R)

                 timeExecution = (datetime.datetime.now()-start).total_seconds()
                 remaining = 1/R - timeExecution
                 if remaining > 0:
                    time.sleep(remaining)

                 timePeriod = (datetime.datetime.now()-start).total_seconds()
                 executionDurations.append(timeExecution)
                 periodDurations.append(timePeriod)

        ############################################################### METRICS CALCULATION


        offeredLoad = ((R*seconds)/(finishSpawningTime - startExperiment).total_seconds())

        if THREADS:

            print("Joining thread....", end="")

            for a in range(0,len(y)):
                if not y[a].is_alive():
                    y[a].join()
                    afterJoined = afterJoined + 1

            print("...finished!")

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


        if folderName!="":
            createFolder(folderName+"/logs")

            for i in range(0,len(logs)):
                with open(folderName+"/logs/log_peer0.org"+str(i+1)+".example.com_r"+str(R)+"_try="+ str(TRY)+".txt", 'a') as f:
                    f.write(logs[i])



        for i in range(1,NUM_ORG+1):
             list = logs[i-1].split("grpc.service=protos.Endorser grpc.method=ProcessProposal")
             j = 0
             for value in list:
                 if (j != 0):
                         if ( len(value.split("grpc.call_duration=")[1].split("ms"))>1 or len(value.split("grpc.call_duration=")[1].split("ms\\n"))>1 ):
                             result=float(value.split("grpc.call_duration=")[1].split("ms")[0].split("s\\n")[0].split("s")[0].split(" ")[0])
                         elif ( len(value.split("grpc.call_duration=")[1].split("s"))>1 or len(value.split("grpc.call_duration=")[1].split("s\\n"))>1 ):
                             result=(float(value.split("grpc.call_duration=")[1].split("ms")[0].split("s\\n")[0].split("s")[0].split(" ")[0]))*1000
                         responses.append(result)
                 j =j+1


             list2 = logs[i-1].split("Committed block [")
             j = 0
             for value in list2:
                    if (j != 0):
                         committedBlocks.append(value.split("]")[0])
                    j =j+1

             print("PEER0.ORG" + str(i) + ".EXAMPLE.COM RESPONSES:" + str(len(responses)) + " Committed Blocks: " + str(len(committedBlocks)))


             list3 = logs[i-1].split("[endorser]")
             j = 0
             for value in list3:
                    if (j != 0):
                         delay = float(value.split("basic duration: ")[1].split(" ")[0].split("ms")[0])
                         id=str(value.split("txID=")[1])[0:8]
                         # print(id + " " + str(delay))
                         # print("")
                         found = 0
                         # print(txIDs)
                         # print(delays)
                         for z in range(0,len(txIDs)):
                             if txIDs[z] == id:
                                 found=1
                                 # print("trovato!")
                                 if delay < delays[z]:
                                     # print("MINORE! " + str(delay) )
                                     delays[z]=delay
                         if found == 0:
                             txIDs.append(id)
                             delays.append(delay)

                    j=j+1


             for u in responses:
                sum= sum + u
             average = sum/(len(responses))
             totalAverage = totalAverage + average

             count = 0
             sum = 0
             responses.clear()
             committedBlocks.clear()


        sum = 0
        for value in CPUoccupation:
                 sum = sum + value

        averageCPUoccupation = sum/len(CPUoccupation)

        sum = 0
        for value in RAMoccupation:
                 sum = sum + value

        averageRAMoccupation = sum/len(RAMoccupation)

        threadStartTimes = [elm for elm in threadStartTimes if isinstance(elm, datetime.datetime)]
        threadFinishTimes = [elm for elm in threadFinishTimes if isinstance(elm, datetime.datetime)]


        firstStart = min(threadStartTimes)
        lastFinish = max(threadFinishTimes)

        throughput = (R*seconds) / ((lastFinish - firstStart).total_seconds())
        endorsementTime=round(statistics.mean(delays),2)
        return Measuration(R,offeredLoad,throughput,totalAverage/NUM_ORG, averageCPUoccupation, averageRAMoccupation,logs,threadStartTimes,endorsementTime)


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


         totalTransactions = 0
         threadStartTimes = []
         threadFinishTimes = []
         transactionDistribution = poissonProcess(R,seconds)
         for value in transactionDistribution:
             totalTransactions = totalTransactions+value

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
                                #print("finished spawning")
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


         for value in results:
            threadStartTimes.append(value[0])
            threadFinishTimes.append(value[1])

         offeredLoad = (totalTransactions/((finishSpawningTime - startExperiment).total_seconds()))

         print("offeredLoad = " + str(offeredLoad))

         print("The first thread has started at " + str(min(threadStartTimes)))

         print("The last thread finished at" + str(max(threadFinishTimes)))


         executor.shutdown(True)


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

              responses.clear()
              print("responses")
              print(len(responses))
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

         print("len threadStartTimes " + len(threadStartTimes))

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



########################################### GRAPH FUNCTIONS ###################################################



def generateSETRATE_OFFEREDLOAD_AEET_CPUOCCUPGraphFromArrays():
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


    x=[1,2,3,4,5,6,7,8,9,10]
    y=[10,13,14,31,61,94,135,184,199,234]
    y_err=[2,1,2,2,13,14,20,11,21,16]

    SETRATE=[1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0,13.0,14.0,15.0,16.0,17.0,18.0,19.0,20.0,21.0,22.0,23.0,24.0]
    FULLOFFEREDLOAD=[1.0,2.0,3.0,3.9,4.9,5.8,6.7,7.7,8.7,9.6,10.7,11.6,12.4,13.5,14.1,14.9,15.3,15.3,15.4,15.6,15.6,15.6,15.4,15.3]
    FULLOFFERED_ERROR=[0.0,0.0,0.1,0.0,0.1,0.1,0.1,0.2,0.2,0.1,0.1,0.2,0.1,0.1,0.4,0.2,0.1,0.4,0.2,0.2,0.3,0.2,0.1,0.1]
    SHORTENEDOFFERED=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
    AEET=[12.15,8.88,7.39,8.51,7.98,7.83,9.57,10.35,12.18,13.74,26.14,36.48,48.51,76.54,89.34,106.52,118.77]
    AEET_ERROR=[4.15,3.01,3.24,0.86,1.41,1.12,1.82,2.61,2.15,0.78,6.07,4.56,14.16,5.89,7.33,10.91,5.61]
    THROUGHPUT=[1.00,2.00,3.00,3.96,4.93,5.92,6.99,7.99,8.92,9.88,10.96,11.81,12.80,13.64,14.62,15.47,16.43]
    ERR_THROUGHPUT=[0.00,0.00,0.00,0.07,0.06,0.06,0.00,0.02,0.08,0.01,0.06,0.07,0.08,0.06,0.06,0.18,0.05]
    CPU_UTILIZ=[11.90,13.60,15.81,18.14,20.36,23.25,26.09,30.32,35.23,41.05,50.46,56.38,65.15,74.51,83.55,91.03,97.61]
    CPU_UTILIZ_ERR=[1.00,0.70,0.62,0.20,0.26,0.11,0.61,1.37,0.59,1.40,3.33,1.38,1.73,1.52,2.54,1.75,0.82]

    plt.figure()
    plt.grid()

    #print(list(map(lambda n: n.offeredLoad,measurations)))

    # ##############################OFFERED LOAD
    #
    plt.axline([0, 0], [1, 1], color=col[2])
    #
    plt.plot(SETRATE,FULLOFFEREDLOAD,'--',linewidth=2 , color=col[1], label='Offered Load[tx/s]' )
    plt.errorbar(SETRATE,FULLOFFEREDLOAD,yerr=FULLOFFERED_ERROR,fmt='x',ecolor = 'red',color='black')

    #
    # plt.plot(list(map(lambda n: n.setRate,measurations)),list(map(lambda n: n.throughput,measurations)),'--',linewidth=2 , color=col[2], label="Throughput[tx/s]" )
    a=25

    plt.xlabel('Set Rate [tx/s]')
    plt.ylim(ymin=0, ymax=max(SETRATE))
    plt.ylabel('Offered Load [tx/s]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("SetRate-OfferedLoad_8org"+type + ".pdf", bbox_inches='tight')
    # plt.savefig("zero-Gamma(10-90)t", bbox_inches='tight')
    # plt.show()
    plt.clf()

    # plt.figure()
    plt.grid()
    #
    #
    # # plt.plot(list(map(lambda n: n.setRate,measurations)),list(map(lambda n: n.offeredLoad,measurations)),'--',linewidth=2 , color=col[1], label=r'Offered Load[tx/s]' )
    #
    # measurations = sorted(measurations, key=lambda x: x.offeredLoad)
    #
    #
    # ######################################### Throughput
    #
    plt.axline([0, 0], [1, 1], color=col[2])

    plt.plot(SHORTENEDOFFERED,THROUGHPUT,'--',linewidth=2 , color=col[1], label="Throughput[tx/s]" )
    plt.errorbar(SHORTENEDOFFERED,THROUGHPUT,yerr=ERR_THROUGHPUT,fmt='x',ecolor = 'red',color='black')

    plt.xlabel('Offered Load [tx/s]')
    plt.ylim(ymin=0, ymax=max(FULLOFFEREDLOAD)*1.1)
    plt.ylabel('Throughput Load [tx/s]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("OfferedLoad-Throughput_8org_"+type+".pdf", bbox_inches='tight')
    # plt.savefig("zero-Gamma(10-90)t", bbox_inches='tight')
    # plt.show()
    plt.clf()
    #
    # ############################## Occupation
    #
    #
    plt.grid()

    plt.plot(SHORTENEDOFFERED,CPU_UTILIZ,'--',linewidth=2 , color=col[1], label="CPU consumption [%]" )
    plt.errorbar(SHORTENEDOFFERED,CPU_UTILIZ,yerr=CPU_UTILIZ_ERR,fmt='x',ecolor = 'red',color='black')

    plt.xlabel('Offered Load [tx/s]')
    plt.ylim(ymin=0, ymax=100)
    plt.ylabel('Occupation [%]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("OfferedLoad-Occupation_8org"+type + ".pdf", bbox_inches='tight')
    # plt.savefig("zero-Gamma(10-90)t", bbox_inches='tight')
    # plt.show()
    plt.clf()


    ############################## AEET

    plt.grid()

    maxAverage = max(AEET)
    plt.plot(SHORTENEDOFFERED,AEET,'--',linewidth=2 , color=col[1], label="Average Endorsement execution Time [ms]" )
    plt.errorbar(SHORTENEDOFFERED,AEET,yerr=AEET_ERROR,fmt='x',ecolor = 'red',color='black')
    plt.xlabel('Offered Load [tx/s]')
    plt.ylim(ymin=0, ymax=maxAverage*1.20)
    plt.ylabel('Average Endorsement execution Time [ms]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("OfferedLoad-AEET_8org"+type + ".pdf", bbox_inches='tight')
    # plt.savefig("zero-Gamma(10-90)t", bbox_inches='tight')
    plt.show()
    plt.clf()

def generate_cpumax_AEET_Graph():
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


    CPU=[2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    AEET=[71.7,54.6,58.8,48.0,34.3,21.5,19.4,15.2,16.5,15.2,14.3,16.8,14.6,16.7,14.7,16.4,13.1,13.4,14.2]
    AEET_ERR=[17.7,3.4,9.7,1.2,3.1,2.4,2.5,2.9,5.2,1.7,1.2,1.8,4.2,3.6,3.3,1.5,1.4,1.6,3.3]

    plt.figure()
    plt.grid()

    #print(list(map(lambda n: n.offeredLoad,measurations)))

    # ##############################OFFERED LOAD
    #
    #plt.axline([0, 0], [1, 1], color=col[2])
    #
    plt.plot(CPU,AEET,'--',linewidth=2 , color=col[1], label='AEET[ms]' )
    plt.errorbar(CPU,AEET,yerr=AEET_ERR,fmt='x',ecolor = 'red',color='black')

    #
    # plt.plot(list(map(lambda n: n.setRate,measurations)),list(map(lambda n: n.throughput,measurations)),'--',linewidth=2 , color=col[2], label="Throughput[tx/s]" )
    a=100

    plt.xlabel('Cpu percentage [%]')
    plt.ylim(ymin=0, ymax=a)
    plt.ylabel('AAET [ms]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("CPU_AEET"+type + ".pdf", bbox_inches='tight')
    # plt.savefig("zero-Gamma(10-90)t", bbox_inches='tight')
    # plt.show()
    plt.clf()



class AEETData:
    def __init__(self, date, endorsementTime):
        self.date = date
        self.endorsementTime = endorsementTime

class QueueData:
    def __init__(self, counterIncrementale,counterIntervallo, AEET,time):
        self.counterIncrementale=counterIncrementale
        self.counterIntervallo=counterIntervallo
        self.queuedRequest = counterIncrementale-counterIntervallo
        self.AEET = round(AEET,2)
        self.time = time
    def toFile(self):
        return "[" + str(self.counterIncrementale) + "; " + str(self.counterIntervallo) + "; " + str(self.queuedRequest) + "; "+ str(self.AEET) + "; "+ str(self.time)  + "]\n"

def generateSETRATE_OFFEREDLOAD_AEET_CPUOCCUPGraphFromASingleFile(measurations,folderName=""):

    ######to modify
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
    a= 25

    plt.xlabel('Set Rate [tx/s]')
    plt.ylim(ymin=0, ymax=max(list(map(lambda n: n.setRate,measurations)))*1.1)
    plt.ylabel('Offered Load [tx/s]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("./" + folderName+"/SetRate-OfferedLoad_8org"+type + ".pdf", bbox_inches='tight')
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
    plt.ylim(ymin=0, ymax=max(list(map(lambda n: n.throughput,measurations)))*1.1)
    plt.ylabel('Throughput Load [tx/s]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("./" + folderName+"/OfferedLoad-Throughput_8org_"+type+".pdf", bbox_inches='tight')
    # plt.savefig("zero-Gamma(10-90)t", bbox_inches='tight')
    # plt.show()
    plt.clf()

    plt.figure()
    plt.grid()

    plt.plot(list(map(lambda n: n.offeredLoad,measurations)),list(map(lambda n: float(n.CPUoccupation),measurations)),'--',linewidth=2 , color=col[1], label="CPU consumption [%]" )
    # plt.plot(list(map(lambda n: n.offeredLoad,measurations)),list(map(lambda n: float(n.RAMoccupation),measurations)),'--',linewidth=2 , color=col[2], label="RAM consumption [%]" )


    plt.xlabel('Offered Load [tx/s]')
    plt.ylim(ymin=0, ymax=100)
    plt.ylabel('Occupation [%]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("./" + folderName+"/OfferedLoad-Occupation_8org"+type + ".pdf", bbox_inches='tight')
    # plt.savefig("zero-Gamma(10-90)t", bbox_inches='tight')
    # plt.show()
    plt.clf()

    plt.figure()
    plt.grid()
    maxAverage = max(list(map(lambda n: n.average,measurations)))

    # plt.axline([0, 0], [8, maxAverage*1.1], color=col[2])

    plt.plot(list(map(lambda n: n.offeredLoad,measurations)),list(map(lambda n: n.average,measurations)),'--',linewidth=2 , color=col[1], label="Average Endorsement execution Time [ms]" )

    plt.xlabel('Offered Load [tx/s]')
    plt.ylim(ymin=0, ymax=maxAverage*1.1)
    plt.ylabel('Average Endorsement execution Time [ms]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("./" + folderName+"/OfferedLoad-AEET_8org"+type + ".pdf", bbox_inches='tight')
    # plt.savefig("zero-Gamma(10-90)t", bbox_inches='tight')
    # plt.show()
    plt.clf()

    plt.figure()
    plt.grid()
    maxEndorsingTIme = max(list(map(lambda n: n.endorsementTime,measurations)))

    # plt.axline([0, 0], [8, maxAverage*1.1], color=col[2])

    plt.plot(list(map(lambda n: n.offeredLoad,measurations)),list(map(lambda n: n.endorsementTime,measurations)),'--',linewidth=2 , color=col[1], label="Average Endorsement Time [ms]" )

    plt.xlabel('Offered Load [tx/s]')
    plt.ylim(ymin=0, ymax=maxEndorsingTIme*1.1)
    plt.ylabel('Average Endorsement Time [ms]')
    # plt.title("Periodic Process")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("./" + folderName+"/OfferedLoad-AET_8org"+type + ".pdf", bbox_inches='tight')
    # plt.savefig("zero-Gamma(10-90)t", bbox_inches='tight')
    # plt.show()
    plt.clf()


#############################################

def queuedRequest_to_AEET_(SELECTION_ALGORITHM,N,CPU):



    #########################GRAPH SETTINGS
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

    #########################MEASURATIONS
    YVECTOR=[]
    XVECTOR=[]
    NUMTRY=2
    R=8
    seconds=10

    folder="serviceStatsOutput/QUEUEDREQUEST_AEET_NUMTRY="+str(NUMTRY)+"R="+str(R)+"SECONDS="+str(seconds)+str(SELECTION_ALGORITHM) + "_" + str(N)+"_"+timestamp()
    cmd = "mkdir " + folder
    createFolderCommand = getCleanSubProcessOutput(cmd)

    with open(folder+ "/queuedRequestAndAEETperSecond.txt" , 'a') as f:

        for w in range(0,NUMTRY):
            data=[]
            measuration = measure_stat_uniform(R,seconds,SELECTION_ALGORITHM,N,CPU+"_"+str(w))

            print(measuration.toString())

            queuedRequestAndAEETperSecond=[]

            for p in range(0,NUM_ORG):
                #########################ENDORSEMENT TIME EXTRACTION
                cleanedList=measuration.logs[p].split("UTC")
                for a in range(0,len(cleanedList)-1):
                    if len(cleanedList[a+1].split("grpc.service=protos.Endorser grpc.method=ProcessProposal"))>1:
                        # date_time_obj=datetime.fromisoformat(str(cleanedList[a].split("[34m")[1]))
                        #date_time_obj = datetime.strptime(, '%y-%m-%d %H:%M:%S.ffff')
                        date_time_obj=datetime.datetime.strptime(str(cleanedList[a].split("[34m")[1].rstrip().replace(" ","_")), "%Y-%m-%d_%H:%M:%S.%f")+datetime.timedelta(hours=2)

                        #print(str(date_time_obj))
                        if len(cleanedList[a+1].split("grpc.service=protos.Endorser grpc.method=ProcessProposal")[1].split("grpc.call_duration=")[1].split("ms"))>1:
                            endorsementTime=float(cleanedList[a+1].split("grpc.service=protos.Endorser grpc.method=ProcessProposal")[1].split("grpc.call_duration=")[1].split("ms")[0])
                        elif len(cleanedList[a+1].split("grpc.service=protos.Endorser grpc.method=ProcessProposal")[1].split("grpc.call_duration=")[1].split("s"))>1:
                            #print(cleanedList[a+1].split("grpc.service=protos.Endorser grpc.method=ProcessProposal")[1])
                            endorsementTime=float(cleanedList[a+1].split("grpc.service=protos.Endorser grpc.method=ProcessProposal")[1].split("grpc.call_duration=")[1].split("s")[0])*1000
                        else:
                            print("ERRORE!")
                        # print("endorsementTime")
                        # print(endorsementTime)
                        data.append(AEETData(date_time_obj,endorsementTime))



                #########################GENERATION TIME PERIODS
                firstEndorsementTime = data[0].date
                lastEndorsementTime = data[-1].date
                for value in data:
                    if value.date <= firstEndorsementTime:
                        firstEndorsementTime=value.date
                    if value.date>= lastEndorsementTime:
                        lastEndorsementTime=value.date
                timeExperiment=(lastEndorsementTime-firstEndorsementTime).total_seconds()
                dateList=[]
                for x in range (0, int(timeExperiment)):
                    dateList.append(firstEndorsementTime + datetime.timedelta(seconds = x))

                #########################COUNTING PENDING REQUEST + AEET FOR EACH SECOND [PENDINGREQUESTS,AEET,t]

                counterIncrementale=0
                counterIntervallo=0
                AEET=0
                base = dateList[0]
                queuedRequests=[]
                AEETperSecond=[]
                for i in range(1,len(dateList)):
                    limit=dateList[i]
                    for value in data:
                        if value.date >=base and value.date<limit:
                            counterIntervallo=counterIntervallo+1
                            AEET=AEET+value.endorsementTime
                    for value in measuration.threadStartTimes:
                        if i!=1:
                            if value >=base and value<limit:
                                counterIncrementale=counterIncrementale+1
                        else:
                            if value<limit:
                                counterIncrementale=counterIncrementale+1
                    #print("counterIntervallo: " + str(counterIntervallo) )
                    #print("counterIncrementale: " + str(counterIncrementale) )

                    #print("AEET: " + str(AEET) )
                    if counterIntervallo>0:
                        queueData=QueueData(counterIncrementale,counterIntervallo,AEET/counterIntervallo,i)
                        queuedRequestAndAEETperSecond.append(queueData)
                        f.write(queueData.toFile())

                    # else:
                    #     queuedRequestAndAEETperSecond.append(QueueData(counterIncrementale-counterIntervallo,-1,i))

                    counterIncrementale=counterIncrementale-counterIntervallo
                    counterIntervallo=0
                    AEET=0
                    base=dateList[i]

                queuedRequests=[]
                AEETperSecond=[]
                dateList=[]
                cleanedList=[]
                data=[]

                ###############FINO A QUI DEVO FARE IL FOR


                #########################GROUPING DATA FOR NUMBER OF PENDING REQUESTS [PENDINGREQUESTS,AEET]

            maxQueuedRequests=max(queuedRequestAndAEETperSecond,key=attrgetter('queuedRequest')).queuedRequest
            AEETperNumberOfQueuedRequest=0
            count=0
            xtemp=[]
            ytemp=[]
            for i in range(0,maxQueuedRequests+1):
                    # print("NUM_REQ----> " +str(i))
                    for value in queuedRequestAndAEETperSecond:
                        if value.queuedRequest==i:
                            AEETperNumberOfQueuedRequest=AEETperNumberOfQueuedRequest+value.AEET
                            count=count+1
                    if count > 0:
                        #w is the index for the try number
                        xtemp.append(i)
                        ytemp.append(round(AEETperNumberOfQueuedRequest/count,2))
                        #print("QUEUED REQUESTS: " + str(i) + "AVGAEET: " + str(AEETperNumberOfQueuedRequest/count))
                    AEETperNumberOfQueuedRequest=0
                    count=0
            XVECTOR.append(xtemp)
            YVECTOR.append(ytemp)
            time.sleep(60)

    #########################GRAPH PLOTTING
    # for i in range(0,NUMTRY):
    #     plt.figure()
    #     plt.grid()
    #     plt.plot(XVECTOR[i],YVECTOR[i],'--',linewidth=2 , color=col[1], label='AEET[ms]' )
    #     a=100
    #
    #     plt.xlabel('Number of queued requests per second [1/s]' )
    #     plt.ylim(ymin=0, ymax=max(YVECTOR[i]))
    #     plt.ylabel('AAET [ms]')
    #     #plt.title("Average Endorsement Execution Time depending on the number of queued requests in a second")
    #     plt.legend(loc='upper left')
    #     plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    #
    #     plt.savefig("./"+folder+"/QueuedRequests_AEET"+str(i)+".pdf", bbox_inches='tight')

############################## AVERAGE PLOT
    ALLX=[]
    AVERAGEX=[]
    AVERAGEY=[]
    AVERAGEERROR=[]
    for i in range(0,len(XVECTOR)):
        ALLX = list(set().union(ALLX,XVECTOR[i]))
    print(ALLX)
    # maxQueuedRequests=max(AVERAGEX)

    AEETperNumberOfQueuedRequest=0
    count=0

    for a in ALLX:
        print("a---->" + str(a) )
        valueForError=[]
        for i in range(0,len(XVECTOR)):
            for j in range(0,len(XVECTOR[i])):
                if XVECTOR[i][j]==a:
                        if count==0:
                            minAEET=YVECTOR[i][j]
                            maxAEET=YVECTOR[i][j]
                        valueForError.append(YVECTOR[i][j])
                        AEETperNumberOfQueuedRequest=AEETperNumberOfQueuedRequest+YVECTOR[i][j]
                        count=count+1
                        if YVECTOR[i][j]<minAEET:
                            minAEET=YVECTOR[i][j]
                        if YVECTOR[i][j]>maxAEET:
                            maxAEET=YVECTOR[i][j]
        if count > 0:
            #w is the index for the try number
            if len(valueForError)>5:
                average=AEETperNumberOfQueuedRequest/count
                AVERAGEX.append(a)
                AVERAGEY.append(round(AEETperNumberOfQueuedRequest/count))
                print("lenght for error:" +str(len(valueForError)))
                ######controllato e funziona secondo la formula della standard deviation
                AVERAGEERROR.append(round(statistics.stdev(valueForError),2))
                print("[")
                for h in valueForError:
                    print(h)
                print("]")

                print("QUEUED REQUESTS: " + str(a) + "AVGAEET: " + str(AEETperNumberOfQueuedRequest/count)+ " ERROR: " + str(statistics.stdev(valueForError)))
    #print("QUEUED REQUESTS: " + sAEET_ERRtr(i) + "AVGAEET: " + str(AEETperNumberOfQueuedRequest/count))
        AEETperNumberOfQueuedRequest=0
        count=0

    plt.figure(figsize=(cm_to_inch(50),cm_to_inch(20)))
    plt.grid()
    plt.plot(AVERAGEX,AVERAGEY,'--',linewidth=2 , color=col[1], label='AEET[ms]' )
    plt.errorbar(AVERAGEX,AVERAGEY,yerr=AVERAGEERROR,fmt='x',ecolor = 'red',color='black')



    plt.xlabel('Number of queued requests per second [1/s]' )
    plt.ylim(ymin=0, ymax=ydimGraph(AVERAGEY,AVERAGEERROR))
    plt.ylabel('AAET [ms]')
    #plt.title("Average Endorsement Execution Time depending on the number of queued requests in a second")
    plt.legend(loc='upper left')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),ncol=3, fancybox=True, shadow=True)
    plt.savefig("./"+folder+"/QueuedRequests_AEET_AVERAGE.pdf", bbox_inches='tight')


    for i in range(0,len(XVECTOR)):
        with open(folder+ "/" + "NUMEXP="+str(i)+".txt" , 'a') as f:
            f.write(toFile(XVECTOR[i],"XVECTOR"))
            f.write(toFile(YVECTOR[i],"YVECTOR"))
    with open(folder+ "/" + "AVERAGE.txt" , 'a') as f:
        f.write(toFile(AVERAGEX,"AVERAGEX"))
        f.write(toFile(AVERAGEY,"AVERAGEY"))
        f.write(toFile(AVERAGEERROR,"AVERAGEERROR"))

def createFolder(folderName):
    cmd = "mkdir " + folderName
    createFolderCommand = getCleanSubProcessOutput(cmd)

def generateThroughput(SELECTION_ALGORITHM,N,CPU):
    NUMEXPERIMENTS=1
    COOLDOWN=200
    folderName="serviceStatsOutput/SETRATE-OFFEREDLOAD-THROUGHPUT-CPUPERC-AEET-ENDORSMEENTTIME_" + timestamp() + "_CPU_"+ CPU+"_"+SELECTION_ALGORITHM + "_" + N+"_NUMTRY="+str(NUMEXPERIMENTS)
    cmd = "mkdir " + folderName
    createFolderCommand = getCleanSubProcessOutput(cmd)

    measurations=[]
    uniformMeasurations = []
    for j in range(0,NUMEXPERIMENTS):
        measurations.append([])

        with open(folderName+"SETRATE-OFFEREDLOAD-THROUGHPUT-CPUPERC-AEET-ENDORSMEENTTIME_" + timestamp() + "_CPU_"+ CPU+"_"+SELECTION_ALGORITHM + "_" + N+"_EXPERIMENT="+str(j)+".txt", 'a') as f:
            for i in range(11,12,1):
                      print("--------------------->" +str(i) )
                      a = measure_stat_uniform(i,100,SELECTION_ALGORITHM,N,CPU+"_"+str(j),folderName)
                      print(a.toString())
                      # print(str(a.endorsementTime))
                      measurations[j].append(a)
                      # uniformMeasurations.append(a)
                      f.write(a.toStructure())
                      #time.sleep(60)

            print("Experiment " + str(j) + " finished.")
            # print(uniformMeasurations)
            # measurations.append(uniformMeasurations)
            # uniformMeasurations.clear()
        #time.sleep(COOLDOWN)

    for value in measurations:
        for x in value:
            print(x.toString())

    finalMeasurations=[]

    for meas in measurations:
        for value in meas:
            finalMeasurations.append(value)
    finalMeasurations.sort(key=lambda x: x.offeredLoad)

    generateSETRATE_OFFEREDLOAD_AEET_CPUOCCUPGraphFromASingleFile(finalMeasurations,folderName)

def generateThroughputFromFile(SELECTION_ALGORITHM,N,CPU):
    NUMEXPERIMENTS=3
    COOLDOWN=200
    folderName="serviceStatsOutput/SETRATE-OFFEREDLOAD-THROUGHPUT-CPUPERC-AEET-ENDORSMEENTTIME_CPU_"+ CPU+"_"+SELECTION_ALGORITHM + "_" + N+"_NUMTRY="+str(NUMEXPERIMENTS)
    cmd = "mkdir " + folderName
    createFolderCommand = getCleanSubProcessOutput(cmd)

    measurations=[]
    uniformMeasurations = []
    for j in range(0,NUMEXPERIMENTS):
        measurations.append([])

        with open(folderName+"/SETRATE-OFFEREDLOAD-THROUGHPUT-CPUPERC-AEET-ENDORSMEENTTIME_CPU_"+ CPU+"_"+SELECTION_ALGORITHM + "_" + N+"_EXPERIMENT="+str(j)+".txt", 'r') as f:
            for row in f:
                data=row.replace("[","").replace("]","").split(";")
                measurations[j].append(Measuration(float(data[0].replace("\n","")),float(data[1].replace("\n","")),float(data[2].replace("\n","")),float(data[3].replace("\n","")),float(data[4].replace("\n","")),float(data[5].replace("\n","")),endorsementTime=float(data[6].replace("\n",""))))


    for value in measurations:
        for x in value:
            print(x.toString())

    finalMeasurations=[]

    for meas in measurations:
        for value in meas:
            finalMeasurations.append(value)
    finalMeasurations.sort(key=lambda x: x.offeredLoad)

    generateSETRATE_OFFEREDLOAD_AEET_CPUOCCUPGraphFromASingleFile(finalMeasurations,folderName)
