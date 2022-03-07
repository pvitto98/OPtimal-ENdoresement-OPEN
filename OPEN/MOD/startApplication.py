import os

DEBUG = True
DONTSHOWOUTPUT = '> /dev/null 2>&1'
MOD_PATH = "../../../OPEN/MOD/"
ORIGINAL_PATH = "../../../OPEN/ORIGINAL/"



if __name__ == '__main__':



  npmInstall = os.system('npm install' + DONTSHOWOUTPUT)

  firstBoot = os.system("ls ./firstBoot.txt | wc -l")

  print(firstBoot)

  if firstBoot == 1:

      clearEnv = os.system('sudo rm -R ./wallet')

      saveDH = os.system('cp ./node_modules/fabric-common/lib/DiscoveryHandler.js ' + ORIGINAL_PATH + 'DiscoveryHandler.js ')
      loadDH = os.system('cp ' + MOD_PATH + 'DiscoveryHandler_MOD.js ./node_modules/fabric-common/lib/DiscoveryHandler.js')

      saveCL = os.system('cp ./node_modules/fabric-common/lib/Client.js ' + ORIGINAL_PATH + 'Client.js ')
      cpyCL = os.system('cp ' + MOD_PATH + 'Client_MOD.js ./node_modules/fabric-common/lib/Client.js')

      saveTR = os.system('cp ./node_modules/fabric-network/lib/transaction.js ' + ORIGINAL_PATH + 'transaction.js ')
      cpyTR = os.system('cp ' + MOD_PATH + 'transaction_MOD.js ./node_modules/fabric-network/lib/transaction.js')

      saveCC = os.system('cp ./../chaincode-javascript/lib/AssetTransfer.js ' + ORIGINAL_PATH + 'AssetTransfer.js ')
      cpyCC = os.system('cp ' + MOD_PATH + 'AssetTransfer_MOD.js ./../chaincode-javascript/lib/AssetTransfer.js')


      rmFB= os.system('rm ./firstBoot.txt')


  appBootup = os.system('node app.js')


################ALSO LINKED TO THE ERROR OF THE WAIT IN CONTRACT
  #createWallet = os.system('mkdir wallet')
  #copyIdentity = os.system('cp ./appUser.id ./wallet/appUser.id')

  #backupIdentity = os.system('cp ./wallet/appUser.id ./')
