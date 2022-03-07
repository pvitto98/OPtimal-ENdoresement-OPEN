#!/bin/bash

MOD_PATH="./OPEN/MOD"
TEST_NET_PATH="./HF/test-network"
ORIGINAL_PATH="./OPEN/ORIGINAL"
APP_PATH="./HF/asset-transfer-basic/application-javascript"
CHAINCODE_PATH="./HF/asset-transfer-basic/chaincode-javascript"


cp ${APP_PATH}/node_modules/fabric-common/lib/DiscoveryHandler.js ${MOD_PATH}/node_modules/fabric-common/lib/DiscoveryHandler_MOD.js
cp ${ORIGINAL_PATH}/DiscoveryHandler.js ${TEST_NET_PATH}/node_modules/fabric-common/lib/DiscoveryHandler.js

cp ${APP_PATH}/node_modules/fabric-common/lib/Client.js ${MOD_PATH}/node_modules/fabric-common/lib/Client_MOD.js
cp ${ORIGINAL_PATH}/Client.js ${TEST_NET_PATH}/node_modules/fabric-common/lib/Client.js

cp ${APP_PATH}/node_modules/fabric-network/lib/transaction.js ${MOD_PATH}/node_modules/fabric-common/lib/transaction_MOD.js
cp ${ORIGINAL_PATH}/transaction.js ${TEST_NET_PATH}/node_modules/fabric-common/lib/transaction.js

cp ${CHAINCODE_PATH}/lib/AssetTransfer.js ${MOD_PATH}/AssetTransfer_MOD.js
cp ${ORIGINAL_PATH}/transaction.js ${CHAINCODE_PATH}/lib/AssetTransfer.js
