# OPtimal-ENdoresement-OPEN for HF 2.2

## MOD Installation 

To install the MOD inside the HF network you must follow these steps:

1. Clone the project using ```git clone https://github.com/pvitto98/OPtimal-ENdoresement-OPEN.git ```.

2. Run ```getReady.sh``` script. This will download Hyperledger Fabric(HF) v2.2 and all the needed binaries.

3. Run ```Add8OrgConf.sh``` script. This will apply the needed configuration to have 8 organizations and the needed files for OPEN.

4. Go to the test-network folder and run ```hyperledgerScript.py``` script (i.g., ```python3 hyperledgerScript.py```), this will start the HF network with the needed configuration. From the proposed menu select option ```Yes, for the application``` by pressing `1`. Wait until the script finishes all the needed tasks by showing another menu. From this menu select `0` to close the program.
 
5. The correctness of the preveios steps can be approved by checking the existance of a file called ```FirstBoot.txt``` inside `asset-transfer-basic/application-javascript` folder.

6. The application can be started by running ```startScript.py``` (i.e., ```python3 startScript.py```), and wait for it to finish.

7. After finishing the application, you will have a folder containing the results in text files. To repeat the tests, it is only needed to re-execute the ```startapplication.py``` script.

## Before committing to GitHub

Before committing there are some mandatory steps
1. Close the editor.
2. Bring network down by using ```./network.sh down``` in test-network.
3. Run ```./saveOPENchanges.sh``` in ```asset-transfer-basic/application-javascript```.
4. Run ```./Remove8OrgConf.sh``` in the main folder.

Be sure to run ```Add8OrgConf.sh``` and ```Remove8OrgConf.sh``` in couple or things will get messed up. by using these commands no modified file will be public on GitHub.


## Additional infos

If an error like ```- error: [DiscoveryService]: send[mychannel] - Channel:mychannel received discovery error:access denied  ``` appeared, you need to remove the wallet folder which is inside `asset-transfer-basic` folder.

