# OPtimal-ENdoresement-OPEN for HF 2.2

## MOD Installation 

To install the MOD inside the HF network you must follow these steps:

* Step 0: Clone the project 

```git clone https://github.com/pvitto98/OPtimal-ENdoresement-OPEN.git --recursive```

The recursive flag is mandatory to download the HF submodule.

* Step 0.1: Enter hf folder and checkout version to 2.2 (git checkout release-2.2)


* Step 1 : Run Add8OrgConf.sh script. This will add the configuration for 8 organizations and some needed files for OPEN.

* Step 2: if needed, install peer binary and configuration files. you can do it by executing the installPeerAndConfiguration.sh file into the HF folder 

* Step 3: Start hf network by going to test-network and running hyperledgerScript.py script (python3 hyperledgerScript.py). 

Select 

``` 1. Yes, for the application.```

 Wait for it to end and then press 0 to close the program.
 
* Step 4: Go to asset-transfer-basic/application-javascript and be sure that there's a file called FirstBoot.txt. If it's not there something could be gone wrong.
  Run startScript.py (through python3 command) and wait for the application to finish.


You can finally open the project on a file editor since all the important files are copied inside the hf network. to boot up the application you need just to re-execute startapplication.py.

## Before committing to GitHub

Before committing there are some mandatory steps
* Step 1: Close the editor
* Step 2: Bring network down by using ./network.sh down in test-network.
* Step 3: Run ./saveOPENchanges.sh in asset-transfer-basic/application-javascript.
* Step 4: Run ./Remove8OrgConf.sh in the main folder.

Be sure to run Add8OrgConf.sh and Remove8OrgConf.sh In couple or things will get messed up. by using these commands no modified file will be public on GitHub.


## Additional infos

If an error like  

```- error: [DiscoveryService]: send[mychannel] - Channel:mychannel received discovery error:access denied  ```

appears you need to remove the wallet folder inside asset-transfer-basic

