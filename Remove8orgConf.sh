#!/bin/bash

MOD_PATH="./OPEN/MOD"
TEST_NET_PATH="./HF/test-network"
ORIGINAL_PATH="./OPEN/ORIGINAL"
APP_PATH="./HF/asset-transfer-basic/application-javascript"

OPENactive=$(ls ./OPENactive.txt | wc -l)

if [ ${OPENactive} -eq 0 ];
then
    echo "OPEN was not initialized. Exiting."
    exit -1
fi

rm ./HF/installPeerAndConfiguration.sh


########## CONFIGTX FOLDER
cp ${TEST_NET_PATH}/configtx/configtx.yaml ${MOD_PATH}/configtx/configtx_MOD.yaml
cp ${ORIGINAL_PATH}/configtx/configtx.yaml ${TEST_NET_PATH}/configtx/configtx.yaml


########## CONFIGURATION FILES
cp -R ${TEST_NET_PATH}/ ${MOD_PATH}/configurationFiles
rm -R ${TEST_NET_PATH}/configurationFiles

################
cp ${TEST_NET_PATH}/hyperledgerScript.py ${MOD_PATH}/hyperledgerScript.py
rm ${TEST_NET_PATH}/hyperledgerScript.py

cp ${TEST_NET_PATH}/configuration.py ${MOD_PATH}/configuration.py
rm ${TEST_NET_PATH}/configuration.py

cp ${TEST_NET_PATH}/network.sh ${MOD_PATH}/network.sh
cp ${ORIGINAL_PATH}/network.sh ${TEST_NET_PATH}/network.sh
#####################qua

################## SCRIPT FOLDER

cp ${TEST_NET_PATH}/scripts/createChannel.sh ${MOD_PATH}//scripts/createChannel_MOD.sh
cp ${ORIGINAL_PATH}/scripts/createChannel.sh ${TEST_NET_PATH}/scripts/createChannel.sh

cp ${TEST_NET_PATH}/scripts/envVar.sh ${MOD_PATH}/scripts/envVar_MOD.sh
cp ${ORIGINAL_PATH}/scripts/envVar.sh ${TEST_NET_PATH}/scripts/envVar.sh

cp ${TEST_NET_PATH}/scripts/setAnchorPeer.sh ${MOD_PATH}/scripts/setAnchorPeer_MOD.sh
cp ${ORIGINAL_PATH}/scripts/setAnchorPeer.sh ${TEST_NET_PATH}/scripts/setAnchorPeer.sh
#
# #

################## ORGANIZATIONS FOLDER
cp ${TEST_NET_PATH}/organizations/ccp-generate.sh ${MOD_PATH}/organizations/ccp-generate_MOD.sh
cp ${ORIGINAL_PATH}/organizations/ccp-generate.sh ${TEST_NET_PATH}/organizations/ccp-generate.sh



############################### CRYPTOGEN
for i in {3..8}
do
  cp ${TEST_NET_PATH}/organizations/cryptogen/crypto-config-org${i}.yaml ${MOD_PATH}/organizations/cryptogen/crypto-config-org${i}.yaml
  rm ${TEST_NET_PATH}/organizations/cryptogen/crypto-config-org${i}.yaml
done

############################### FABRIC-CA


################# TO DOUBLE CHECK THE PORT NUMBER 7054

cp ${TEST_NET_PATH}/organizations/fabric-ca/org2/fabric-ca-server-config.yaml ${MOD_PATH}/organizations/fabric-ca/org2/fabric-ca-server-config_MOD.yaml
cp ${ORIGINAL_PATH}/organizations/fabric-ca/org2/fabric-ca-server-config.yaml ${TEST_NET_PATH}/organizations/fabric-ca/org2/fabric-ca-server-config.yaml



for i in {3..8}
do
  cp -r ${TEST_NET_PATH}/organizations/fabric-ca/ ${MOD_PATH}/organizations/fabric-ca/org${i}
  rm -R ${TEST_NET_PATH}/organizations/fabric-ca/org${i}
done

cp ${TEST_NET_PATH}/organizations/fabric-ca/registerEnroll.sh ${MOD_PATH}/organizations/fabric-ca/registerEnroll_MOD.sh
cp ${ORIGINAL_PATH}/organizations/fabric-ca/registerEnroll.sh ${TEST_NET_PATH}/organizations/fabric-ca/registerEnroll.sh




################################### DOCKER FOLDER
cp ${TEST_NET_PATH}/docker/docker-compose.yaml ${MOD_PATH}/docker/docker-compose.yaml
rm ${TEST_NET_PATH}/docker/docker-compose.yaml

cp ${TEST_NET_PATH}/docker/docker-compose-ca.yaml ${MOD_PATH}/docker/docker-compose-ca_MOD.yaml
cp ${ORIGINAL_PATH}/docker/docker-compose-ca.yaml ${TEST_NET_PATH}/docker/docker-compose-ca.yaml

cp ${TEST_NET_PATH}/docker/docker-compose-test-net.yaml ${MOD_PATH}/docker/docker-compose-test-net_MOD.yaml
cp ${ORIGINAL_PATH}/docker/docker-compose-test-net.yaml ${TEST_NET_PATH}/docker/docker-compose-test-net.yaml

cp ${TEST_NET_PATH}/docker/.env ${MOD_PATH}/docker/.env
rm ${TEST_NET_PATH}/docker/.env

################################ APPLICATION FOLDER

cp ${APP_PATH}/app.js ${MOD_PATH}/app_MOD.js
cp ${ORIGINAL_PATH}/app.js ${APP_PATH}/app.js



rm ${APP_PATH}/startApplication.py
rm ${APP_PATH}/saveOPENchanges.sh
rm ${APP_PATH}/bootup.sh

rm -R ${APP_PATH}/results
rm -R ${APP_PATH}/wallet
