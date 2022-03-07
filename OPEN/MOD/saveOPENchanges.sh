#!/bin/bash

MOD_PATH="../../../OPEN/MOD"
TEST_NET_PATH="../test-network"
ORIGINAL_PATH="../../../OPEN/ORIGINAL"
APP_PATH="./"
CHAINCODE_PATH="../chaincode-javascript"


cp ${APP_PATH}/node_modules/fabric-common/lib/DiscoveryHandler.js ${MOD_PATH}/DiscoveryHandler_MOD.js
cp ${ORIGINAL_PATH}/DiscoveryHandler.js ${APP_PATH}/node_modules/fabric-common/lib/DiscoveryHandler.js
#
cp ${APP_PATH}/node_modules/fabric-common/lib/Client.js ${MOD_PATH}/Client_MOD.js
cp ${ORIGINAL_PATH}/Client.js ${APP_PATH}/node_modules/fabric-common/lib/Client.js
#
cp ${APP_PATH}/node_modules/fabric-network/lib/transaction.js ${MOD_PATH}/transaction_MOD.js
cp ${ORIGINAL_PATH}/transaction.js ${APP_PATH}/node_modules/fabric-common/lib/transaction.js

cp ${CHAINCODE_PATH}/lib/assetTransfer.js ${MOD_PATH}/assetTransfer_MOD.js
cp ${ORIGINAL_PATH}/assetTransfer.js ${CHAINCODE_PATH}/lib/AssetTransfer.js
