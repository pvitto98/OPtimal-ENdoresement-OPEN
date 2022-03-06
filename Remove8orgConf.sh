
MOD_PATH="./OPEN/MOD"
TEST_NET_PATH="./HF/test-network"
ORIGINAL_PATH="./OPEN/ORIGINAL"

############ CONFIGTX FOLDER
cp ${ORIGINAL_PATH}/configtx/configtx.yaml ${TEST_NET_PATH}/configtx/configtx.yaml

########### CONFIGURATION FILES
rm -R ${TEST_NET_PATH}/configurationFiles
################
rm ${TEST_NET_PATH}/hyperledgerScript.py
rm ${TEST_NET_PATH}/configuration.py

cp ${ORIGINAL_PATH}/network.sh ${TEST_NET_PATH}/network.sh
#####################qua

################### SCRIPT FOLDER


cp ${ORIGINAL_PATH}/scripts/createChannel.sh ${TEST_NET_PATH}/scripts/createChannel.sh

cp ${ORIGINAL_PATH}/scripts/envVar.sh ${TEST_NET_PATH}/scripts/envVar.sh

cp ${ORIGINAL_PATH}/scripts/setAnchorPeer.sh ${TEST_NET_PATH}/scripts/setAnchorPeer.sh
#
#

################## ORGANIZATIONS FOLDER

cp ${ORIGINAL_PATH}/organizations/ccp-generate.sh ${TEST_NET_PATH}/organizations/ccp-generate.sh



############################### CRYPTOGEN
for i in {3..8}
do
  rm ${TEST_NET_PATH}/organizations/cryptogen/crypto-config-org${i}.yaml
done

############################### FABRIC-CA


################### TO DOUBLE CHECK THE PORT NUMBER 7054

cp ${ORIGINAL_PATH}/organizations/fabric-ca/org2/fabric-ca-server-config.yaml ${TEST_NET_PATH}/organizations/fabric-ca/org2/fabric-ca-server-config.yaml



for i in {3..8}
do
  rm -R ${TEST_NET_PATH}/organizations/fabric-ca/org${i}
done

cp ${ORIGINAL_PATH}/organizations/fabric-ca/registerEnroll.sh ${TEST_NET_PATH}/organizations/fabric-ca/registerEnroll.sh




################################### DOCKER FOLDER
rm ${TEST_NET_PATH}/docker/docker-compose.yaml

cp ${ORIGINAL_PATH}/docker/docker-compose-ca.yaml ${TEST_NET_PATH}/docker/docker-compose-ca.yaml

cp ${ORIGINAL_PATH}/docker/docker-compose-test-net.yaml ${TEST_NET_PATH}/docker/docker-compose-test-net.yaml

rm ${TEST_NET_PATH}/docker/.env
