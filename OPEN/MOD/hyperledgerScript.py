###### TO COLLAPSE EVERYTHING ON ATOM ALT+CTRL+SHIFT+[

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
from configuration import *
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from scipy.stats import poisson
import seaborn as sb#from utils import *

import numpy as np



########################################### FILE NAME + MACRO ###################################################

##create conf
# discover --configFile conf.yaml --peerTLSCA peers/peer0.org1.example.com/tls/ca.crt --userKey msp/keystore/811f0e1efedb8b5d176d7b4bc5881230089eff2a616a51ae6415e73e3be12256_sk --userCert msp/signcerts/User1\@org1.example.com-cert.pem  --MSP Org1MSP saveConfig


ENABLE_NETWORK_CONFIGURATION = False
MODE = "htb"

DONTSHOWOUTPUT = '> /dev/null 2>&1'


def calculateEndorsmentGraph():
     endorsmentDelays=[]


     for i in range(1,9):
         port = int((i*2)+5)

         name = "./../asset-transfer-basic/application-javascript/endorsmentDelays/peer0.org"+ str(i) + ".example.com:"+str(port)+"051.txt"
         endorsmentdelaysFile = open(name, 'r')

         first = True
         for row in endorsmentdelaysFile:
             if(first):
                 TOTAL_TXS = int(row.replace("\n","").replace(".",","))
                 first=False
             else:
                 endorsmentDelays.append(int(float(row.replace("\n",""))))

         for j in range(0,TOTAL_TXS - len(endorsmentDelays)):
             endorsmentDelays.append(-1)

         #bins = range(0, TOTAL_TXS, 1)
         plt.hist(endorsmentDelays, 20 , histtype="barstacked")

         #plt.bar(bins, endorsmentDelays, width=1, edgecolor="black", linewidth=0.5)
         plt.title("peer0.org"+str(i)+".example.com")

         plt.xlabel("txs")
         plt.xlabel("Endorse Time [ms]", fontsize = 7)
         folderName = timestamp()

         plt.savefig("endorsmentDelaysOutput/delays"+str(i)+".jpeg")
         plt.clf()

         bins = range(0,50, 1)
         plt.hist( endorsmentDelays, bins, histtype="barstacked")
         plt.title("peer0.org"+str(i)+".example.com")
         plt.xlabel("Endorse Time [ms]", fontsize = 7)
         plt.ylabel("Count", fontsize = 7)
         plt.savefig("endorsmentDelaysOutput/delays"+str(i)+"hist_noOutliers.jpeg")
         plt.clf()
         endorsmentDelays.clear()


     exit(0)



def printOptions():
      print("0 - Close the program")
      print("1 - Measure endorsing time")
      print("2 - Perform a network test")
      print("3 - Compute service stats")
      val = input("Choose: ")
      if not val.isnumeric():
        val = -1
      return val

if __name__ == '__main__':

  print("[SCRIPT] : HyperLedger script has been started.")

  finished = False
  while (finished == False):
      print("Do you want to boot-up the network?")
      print("0 - No")
      print("1 - Yes, for the application")
      print("2 - Yes, for testing purpouses")
      print("3 - Additinal functionalities")

      val = input("Choose: ")

      startBootup  = datetime.datetime.now()


      if (int(val) == 0):
          print("")
          print("You decided to leave the actual configuration.")
          print("")

          # containers = Container.loadConf()
          # isAlreadyDeployed(containers)
          containers = generateContainerBridgeInfoFile()

          finished=True

      elif (int(val) == 1):
          print("")
          print("You decided to boot up HyperLedger for the application (who needs Fabric-Ca certifications). ")
          print("")

          HFBootDown = os.system('./network.sh down')
          HFBootup = os.system('./network.sh up createChannel -c mychannel -ca')
          HFCreateChannel = os.system('./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript/ -ccl javascript')


          containers = generateContainerBridgeInfoFile()
          finished=True

      elif (int(val) == 2 ):
          print("")
          print("You decided to boot up freshly HyperLedger Fabric.")
          HFBootup = os.system('./network.sh full')

          containers = generateContainerBridgeInfoFile()
          finished=True

      elif (int(val) == 3 ):
          print("")
          print("You decided the experimental launch.")
          # HFBootDown = os.system('./network.sh down')
          # HFBootup = os.system('./network.sh up createChannel -c mychannel -ca')
          # HFCreateChannel = os.system('./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript/ -ccl javascript')

          containers = generateContainerBridgeInfoFile_SmartContract()
          for container in containers:
              print(container.toString())
          generateNetworkConf(containers, MODE)

          pingTestDelays(containers)

          finished=True

      else:
          print("Wrong value. Retry.")
          print("")


  if (checkDelaySymmetry(containers) != 0):
      print("")
      print("[ERROR]: You should check the delays. They are not symmetrical. ")

  if (checkBandwidthSymmetry(containers) != 0):
    print("")
    print("[WARNING]: You should check the bandwidth. They are probably not symmetric or the upper bandwidth is not big enough.")

  if (int(val) == 1 or int(val)==2) and ENABLE_NETWORK_CONFIGURATION:
      generateNetworkConf(containers, MODE)

  if (int(val) == 1):
      print("")
      print("Done! You now need to go fabric-samples/asset-transfer-basic/application-javascript and run the startApplication.py script.")
      print("")

  endBootUp = datetime.datetime.now()

  print("Boot-up took " + str((endBootUp - startBootup).total_seconds()) + " seconds.")
  finished = False
  while finished == False:

      print("What do you would like to do: ")
      val = printOptions()
      if (val!= -1):

          if (int(val) == 0 ):
            Container.saveConf(containers)
            finished = True

          elif (int(val) == 1):
            measureEndorsingTime("ONEMINTIME")

          elif (int(val) == 2):
            print("")
            finished2 = False
            while finished2 == False:
                  print("0 - Do the ping test")
                  print("1 - Do the iperf test")
                  print("2 - Go back")
                  val2 = input("Choose: ")

                  if (int(val2) == 0 ):
                    pingTestDelays(containers)

                  elif (int(val2) == 1):
                    iperfTest(containers)

                  else:
                      if(int(val2) != 2):
                        print("Value not correct. Retry.")
                      else:
                        print("")
                        finished2 = True

          elif (int(val) == 3):
              Actualtimestamp = timestamp()
              seconds = 100
              maxR = 15
              folderName = Actualtimestamp + "uniformAndPoissonMeasurations"
              cmd = "mkdir serviceStatsOutput/" + folderName

              createFolderCommand = getCleanSubProcessOutput(cmd)
              # print("UNIFORM MEASURATION")
              # uniformMeasurations = []
              #
              # with open("serviceStatsOutput/"+folderName+"/uniformMeasurations.txt", 'a') as f:
              #     for i in range(1,maxR,1):
              #         print("--------------------->" +str(i) )
              #         a = measure_stat_uniform(i,seconds)
              #         print(a.toString())
              #         uniformMeasurations.append(a)
              #         f.write(a.toString())
              #         time.sleep(60)

               # e.g. double each n


              #
              # plt.plot(list(map(lambda n: n.setRate, uniformMeasurations)), list(map(lambda n: n.actualRate, uniformMeasurations)), marker = 'o')
              #
              # plt.title("Working Environment - Uniform")
              # plt.xlabel("Set Rate [tx/s]", fontsize = 7)
              # plt.ylabel("Actual Rate [tx/s]", fontsize = 7)
              # for i,j in zip(list(map(lambda n: n.setRate, uniformMeasurations)),list(map(lambda n: n.actualRate, uniformMeasurations))):
              #     plt.annotate("{:.2f}".format(j),xy=(i,j+0.35))
              # plt.savefig("serviceStatsOutput/"+folderName+"/ActualRatevsSetRateplotUniform.jpeg")
              # plt.clf()
              #
              # plt.plot(list(map(lambda n: n.actualRate, uniformMeasurations)), list(map(lambda n: n.average, uniformMeasurations)), marker = 'o')
              #
              # plt.title("Queueing on Peers - Uniform")
              # plt.xlabel("Set Rate[tx/s]", fontsize = 7)
              # plt.ylabel("Average Response time[ms]", fontsize = 7)
              # for i,j in zip(list(map(lambda n: n.setRate, uniformMeasurations)),list(map(lambda n: n.average, uniformMeasurations))):
              #     plt.annotate("{:.2f}".format(j),xy=(i,j+0.35))
              # plt.savefig("serviceStatsOutput/"+folderName+"/ActualRateandResponseTimeplotUniform.jpeg")
              # plt.clf()
              #
              #
              #
              print("POISSON MEASURATION")
              poissonMeasurations = []

              with open("serviceStatsOutput/"+folderName+"/poissonMeasurations.txt", 'a') as f:
                  for i in range(1,maxR,1):
                      a = measure_stat_poisson(i,seconds)
                      print(a.toString())
                      poissonMeasurations.append(a)
                      f.write(a.toStructure())
                      time.sleep(60)
          elif (int(val) == 4):
                   print("entrato")
                   measurations = []
                   with open("./poissonMeasurations.txt", 'r') as f:
                       for row in f:
                           l = row.split(";")
                           measurations.append(Measuration(l[0].replace("[",""),l[1],l[2],l[3],l[4],l[5].replace("]","")))
                   generate_offeredLoad_throughput_graph(measurations)
              #     for value in poissonMeasurations:
              #         f.write(value.toString())

              #
              #
              #  # e.g. double each n
              #
              # # plt.plot(list(map(lambda n: n.setRate, poissonMeasurations)), list(map(lambda n: n.actualRate, poissonMeasurations)), marker = 'o')
              #
              # createFolderCommand = getCleanSubProcessOutput(cmd)
              # # plt.title("Working Environment - Poisson")
              # # plt.xlabel("Set Rate [tx/s]", fontsize = 7)
              # # plt.ylabel("Actual Rate [tx/s]", fontsize = 7)
              # # for i,j in zip(list(map(lambda n: n.setRate, poissonMeasurations)),list(map(lambda n: n.actualRate, poissonMeasurations))):
              # #     plt.annotate("{:.2f}".format(j),xy=(i,j+0.35))
              # # plt.savefig("serviceStatsOutput/"+folderName+"/ActualRatevsSetRateplotPoisson.jpeg")
              # # plt.clf()
              # #
              # # plt.plot(list(map(lambda n: n.actualRate, poissonMeasurations)), list(map(lambda n: n.average, poissonMeasurations)), marker = 'o')
              #
              # with open("serviceStatsOutput/"+folderName+"/uniformMeasurations.txt", 'a') as f:
              #     for value in uniformMeasurations:
              #         f.write(value.toString())
              #
              #
              #
              # # plt.title("Queueing on Peers - Poisson")
              # # plt.xlabel("Set Rate [tx/s]", fontsize = 7)
              # # plt.ylabel("Average Response time[ms]", fontsize = 7)
              # # for i,j in zip(list(map(lambda n: n.setRate, poissonMeasurations)),list(map(lambda n: n.average, poissonMeasurations))):
              # #     plt.annotate("{:.2f}".format(j),xy=(i,j+0.35))
              # # plt.savefig("serviceStatsOutput/"+folderName+"/ActualRateandResponseTimeplotPoisson.jpeg")
              # # plt.clf()
              # # uniformFile = open(, "w")
              # # poissonFile = open("serviceStatsOutput/"+folderName+"/poissonMeasurations.txt", "w")
              #
              #
              # with open("serviceStatsOutput/"+folderName+"/poissonMeasurations.txt", 'a') as f:
              #     for value in poissonMeasurations:
              #         f.write(value.toString())

              # for value in uniformMeasurations:
              #     print(value.toString())
              #     uniformFile.write(value.toString())
              #
              # for value in poissonMeasurations:
              #     print(value.toString())
              #
              #     poissonFile.write(value.toString())

      else:
          print("Value not correct. Retry.")
          print("")
