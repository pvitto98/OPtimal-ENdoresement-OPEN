import os

DEBUG = True
DONTSHOWOUTPUT = '> /dev/null 2>&1'
MOD_PATH = "../../../OPEN/MOD/"
ORIGINAL_PATH = "../../../OPEN/ORIGINAL/"



if __name__ == '__main__':


  npmInstall = os.system('npm install' + DONTSHOWOUTPUT)

  bootup = os.system('./bootup.sh')

  appBootup = os.system('node app.js')


################ALSO LINKED TO THE ERROR OF THE WAIT IN CONTRACT
  #createWallet = os.system('mkdir wallet')
  #copyIdentity = os.system('cp ./appUser.id ./wallet/appUser.id')

  #backupIdentity = os.system('cp ./wallet/appUser.id ./')
