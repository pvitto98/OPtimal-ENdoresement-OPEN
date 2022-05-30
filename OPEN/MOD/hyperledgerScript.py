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
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from scipy.stats import poisson
import seaborn as sb#from utils import *
import sys
import numpy as np
from OLDconfiguration import *
from configuration import *


########################################### FILE NAME + MACRO ###################################################

##create conf
# discover --configFile conf.yaml --peerTLSCA peers/peer0.org1.example.com/tls/ca.crt --userKey msp/keystore/811f0e1efedb8b5d176d7b4bc5881230089eff2a616a51ae6415e73e3be12256_sk --userCert msp/signcerts/User1\@org1.example.com-cert.pem  --MSP Org1MSP saveConfig


ENABLE_NETWORK_CONFIGURATION = False
MODE = "htb"

DONTSHOWOUTPUT = '> /dev/null 2>&1'



def printOptions():
      print("0 - Close the program")
      print("1 - Boot up with JS asset-transfer-basic chaincode.")
      print("2 - Boot up with standard GO chaincode.")
      print("3 - Measure AEET with uniform process.")
      print("6 - AEET with respect to the queued transactions.")
      print("7 - Limit CPU percentage.")

      val = input("Choose: ")
      if not val.isnumeric():
        val = -1
      return val

if __name__ == '__main__':

  print("[SCRIPT] : HyperLedger script has been started.")
  requestRoot = os.system('sudo echo')


  finished = False
  while (finished == False):

      PRESELECTED_VALUE= sys.argv[1]
      ######## python3 HyperLedgerScript.py VALORE_PRESELEZIONATO RND N  INPUTMAXCPUSET[DEFAULT 0]
      if ( sys.argv[1] != str(0) ):
          val=PRESELECTED_VALUE
          print("PRESELECTED VALUE ------------------> " + PRESELECTED_VALUE)
      else:
          val=printOptions()


      if (int(val) == 0):
          print("")
          print("You decided to leave.")
          print("")
          #
          # containers = Container.loadConf()
          # isAlreadyDeployed(containers)
          # containers = generateContainerBridgeInfoFile()

          finished=True

      elif (int(val) == 1):
          time.sleep(1)

          print("")
          print("You decided to boot up HyperLedger with the asset-transfer-basic JS chaincode. ")
          print("")

          HFBootDown = os.system('./network.sh down')
          HFBootup = os.system('./network.sh up createChannel -c mychannel -ca')
          HFCreateChannel = os.system('./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript/ -ccl javascript')
          # HFBootApp = os.system('cd ../asset-transfer-basic/application-javascript && python3 startApplication.py')
          print("")
          # print("Done! You now need to go fabric-samples/asset-transfer-basic/application-javascript and run the startApplication.py script.")
          print("")
      elif (int(val) == 2 ):
          time.sleep(1)
          print("")
          print("You decided to boot up HyperLedger Fabric with standard GO chaincode.")
          HFBootup = os.system('./network.sh full')

      elif (int(val) == 3 ):
            generateThroughputFromFile(SELECTION_ALGORITHM,N,sys.argv[4])

      elif (int(val) == 4):
              generateSETRATE_OFFEREDLOAD_AEET_CPUOCCUPGraphFromArrays()

      elif (int(val) == 5):
              generate_cpumax_AEET_Graph()

      elif (int(val) == 6):
              queuedRequest_to_AEET_(sys.argv[2],sys.argv[3],sys.argv[4])

      elif(int(val) == 7):
              limitCPU(10)

      elif(int(val) == 8):
          n=8
          sum = 0

          for k in range(1,n+1):
              print(k)
              # sum=sum+(math.factorial(n)/(math.factorial(n-k)*math.factorial(k)))
              sum=pow(n,k)
              print(str(k) + " " + str(sum))
          print(sum)

      else:
          print("Wrong value. Retry.")
          print("")

      if (PRESELECTED_VALUE!=0):
         finished=True
