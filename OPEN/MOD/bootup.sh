#!/bin/bash

ORIGINAL_PATH="../../../OPEN/ORIGINAL/"
MOD_PATH="../../../OPEN/MOD/"

  firstBoot=$(sudo ls ./firstBoot.txt | wc -l)
  if [ ${firstBoot} -eq 1 ];
  then

      sudo rm -R ./wallet

      cp ./node_modules/fabric-common/lib/DiscoveryHandler.js ${ORIGINAL_PATH}/DiscoveryHandler.js
      cp  ${MOD_PATH}/DiscoveryHandler_MOD.js ./node_modules/fabric-common/lib/DiscoveryHandler.js

      cp ./node_modules/fabric-common/lib/Client.js ${ORIGINAL_PATH}/Client.js
      cp  ${MOD_PATH}/Client_MOD.js ./node_modules/fabric-common/lib/Client.js

      cp ./node_modules/fabric-network/lib/transaction.js ${ORIGINAL_PATH}/transaction.js
      cp  ${MOD_PATH}/transaction_MOD.js ./node_modules/fabric-network/lib/transaction.js

      cp ./../../chaincode-javascript/lib/assetTransfer.js ${ORIGINAL_PATH}/assetTransfer.js
      cp ${MOD_PATH}/assetTransfer_MOD.js ./../../chaincode-javascript/lib/assetTransfer.js

      rm ./firstBoot.txt
  fi
