# OPtimal-ENdoresement-OPEN for HF 2.2

## Installation

FIRST RULE: DON'T EVER COMMIT OR PUSH HF FOLDER.

###STEP 0: CLONE THE PROJECT (git clone https://github.com/pvitto98/OPtimal-ENdoresement-OPEN.git --recursive). THE RECURSVIE FLAG IS MANDATORY TO DOWNLOAD HF SUBMODULE.
###STEP 0.1: ENTER HF FOLDER AND CHECKOUT VERSION TO 2.2 (git checkout release-2.2)


###STEP 1 : RUN Add8OrgConf.sh SCRIPT. THIS WILL ADD THE CONFIGURATION FOR 8 ORGANIZATION AND SOME NEEDED FILE FOR OPEN.

###STEP 1.1 : IF NEEDED, INSTALL PEER BINARY AND CONFIGURATION FILES. YOU CAN DO IT BY EXECUTING installPeerAndConfiguration.sh FILE INTO HF FOLDER 

###STEP 2: START HF NETWORK BY GOING TO TEST-NETWORK AND RUNNING hyperledgerScript.py SCRIPT (python3 hyperledgerScript.py). SELECT 1. YES, FOR THE APPLICATION. WAIT IT TO END AND THEN PRESS 0.

###STEP 3: GO TO ASSET-TRANSFER-BASIC/APPLICATION-JAVASCRIPT AND BE SURE THAT THERE'S A FILE CALLED FirstBoot.txt. IF IT'S NOT THERE SOMETHING COULD BE GONE WRONG. RUN startScript.py (THROUGH python3 COMMAND) AND WAIT THE APPLICATION TO FINISH.


#### NOW SINCE NOW IT'S LIKE THE NETWORK IS ALREADY MODIFIED. YOU CAN MODIFY FILE INSIDE THE HF FOLDER. ONLY NOW YOU CAN OPEN THE PROJECT ON A FILE EDITOR.

### STEP 4: BEFORE COMMITTING THERE ARE SOME MANDATORY STEPS
#### STEP 4.1: CLOSE THE EDITOR
#### STEP 4.1: BRING NETWORK DOWN BY USING ./network.sh down IN TEST-NETWORK.
#### STEP 4.1: RUN ./saveOPENchanges.sh IN ASSET-TRANSFER-BASIC/APPLICATION-JAVASCRIPT.
#### STEP 4.2: RUN ./Remove8OrgConf.sh IN THE MAIN FOLDER.


### BE SURE TO RUN Add8OrgConf.sh AND Remove8OrgConf.sh IN COUPLE OR THINGS WILL GET MESSED UP. BY USING THESE COMMAND NO MODIFIED FILE WILL BE PUBLIC ON GITHUB

#### IF AN ERROR LIKE THIS APPEARS (2022-03-07T14:31:52.633Z - error: [DiscoveryService]: send[mychannel] - Channel:mychannel received discovery error:access denied YOU NEED TO REMOVE WALLET FOLDER INSIDE ASSET-TRANSFER-BASIC



