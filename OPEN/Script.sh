
MOD_PATH = "./OPEN/MOD"
TEST_NET_PATH = "./HF/test-network"
ORIGINAL_PATH = "./OPEN/ORIGINA"

############ CONFIGTX FOLDER
cp ${TEST_NET_PATH}/configtx/configtx.yaml ${ORIGINAL_PATH}/configtx/configtx.yaml
cp ${MOD_PATH}/configtx/configtx_MOD.yaml ${TEST_NET_PATH}/configtx/configtx.yaml

############ CONFIGURATION FILES
cp ${MOD_PATH}/configurationFiles ${TEST_NET_PATH}

cp ${MOD_PATH}/hyperledgerScript.py ${TEST_NET_PATH}
cp ${MOD_PATH}/configuration.py ${TEST_NET_PATH}

cp ${TEST_NET_PATH}/network.sh ${ORIGINAL_PATH}/network.sh
cp ${MOD_PATH}/network_MOD.sh ${TEST_NET_PATH}/network.sh

#################### SCRIPT FOLDER

cp ${TEST_NET_PATH}/scripts/createChannel.sh ${ORIGINAL_PATH}/scripts/createChannel.sh
cp ${MOD_PATH}/scripts/createChannel_MOD.sh ${TEST_NET_PATH}/scripts/createChannel.sh

cp ${TEST_NET_PATH}/scripts/envVar.sh ${ORIGINAL_PATH}/scripts/envVar.sh
cp ${MOD_PATH}/scripts/envVar_MOD.sh ${TEST_NET_PATH}/scripts/envVar.sh

cp ${TEST_NET_PATH}/scripts/setAnchorPeer.sh ${ORIGINAL_PATH}/scripts/setAnchorPeer.sh
cp ${MOD_PATH}/scripts/setAnchorPeer_MOD.sh ${TEST_NET_PATH}/scripts/setAnchorPeer.sh


################### ORGANIZATIONS FOLDER

cp ${TEST_NET_PATH}/organizations/ccp-generate.sh ${ORIGINAL_PATH}/organizations/ccp-generate.sh
cp ${MOD_PATH}/organizations/ccp-generate_MOD.sh ${TEST_NET_PATH}/organizations/ccp-generate.sh

cp ${TEST_NET_PATH}/organizations/ccp-generate.sh ${ORIGINAL_PATH}/organizations/ccp-generate.sh
cp ${MOD_PATH}/organizations/ccp-generate_MOD.sh ${TEST_NET_PATH}/organizations/ccp-generate.sh


############################### CRYPTOGEN
for i in {3..8}
do
  cp ${MOD_PATH}/organizations/cryptogen/crypto-config-org${i}.yaml ${TEST_NET_PATH}/organizations/cryptogen/crypto-config-org${i}.yaml
done

############################### FABRIC-CA


################### TO DOUBLE CHECK THE PORT NUMBER 7054
cp ${MOD_PATH}/organizations/fabric-ca/org${i}/fabric-ca-server-config.yaml  ${TEST_NET_PATH}/organizations/fabric-ca/org${i}/fabric-ca-server-config.yaml


for i in {3..8}
do
  mkdir ${TEST_NET_PATH}/organizations/fabric-ca/org${i}
  cp ${MOD_PATH}/organizations/fabric-ca/org${i}/fabric-ca-server-config.yaml  ${TEST_NET_PATH}/organizations/fabric-ca/org${i}/fabric-ca-server-config.yaml
done

cp ${TEST_NET_PATH}/organizations/fabric-ca/registerEnroll.sh ${ORIGINAL_PATH}/organizations/fabric-ca/registerEnroll.sh

cp ${MOD_PATH}/organizations/fabric-ca/registerEnroll_MOD.sh  ${TEST_NET_PATH}/organizations/fabric-ca/registerEnroll.sh



################################### DOCKER FOLDER
cp ${MOD_PATH}/docker/docker-compose.yaml ${TEST_NET_PATH}/docker/docker-compose.yaml

cp ${TEST_NET_PATH}/docker/docker-compose-ca.yaml ${ORIGINAL_PATH}/docker/docker-compose-ca.yaml
cp ${MOD_PATH}/docker/docker-compose-ca_MOD.yaml ${TEST_NET_PATH}/docker/docker-compose-ca.yaml

cp ${TEST_NET_PATH}/docker/docker-compose-test-net.yaml ${ORIGINAL_PATH}/docker/docker-compose-test-net.yaml
cp ${MOD_PATH}/docker/docker-compose-test-net_MOD.yaml ${TEST_NET_PATH}/docker/docker-compose-test-net.yaml
