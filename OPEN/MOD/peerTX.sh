#!/bin/bash

source scripts/utils.sh
. scripts/envVar.sh

NUM_ORG=8
# Environment variables for Org1
export PATH=${PWD}/../bin:$PATH
export FABRIC_CFG_PATH=$PWD/../config/

export CORE_PEER_TLS_ENABLED=true

# Initializing the ledger.
function initTheLedger() {
  infoln "######## Initializing the Ledger... ########"
  set -x
  peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic $PEER_DATA -c '{"function":"InitLedger","Args":[]}'
  res=$?
  set +x
  if [ $res -ne 0 ]; then
    errorln "Failed to initialize Ledger...!"
    exit 1
  else
    successln "Initialize Ledger Done!"
  fi
}

# Query the ledger.
function queryLedgerAll() {
  set -x
  # peer chaincode query -C mychannel -n basic -c '{"Args":["GetAllDatas"]}'
  peer chaincode query -C mychannel -n basic -c '{"Args":["GetAllAssets"]}'
  res=$?
  set +x
  if [ $res -ne 0 ]; then
    errorln "Failed to full query of the Ledger...!"
    exit 1
  else
    successln "Full query of the Ledger Done!"
  fi
}

# Updating the world state and the Ledger
function updateLedger() {
  set -x
  # peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic $PEER_DATA -c "{\"function\":\"UpdateData\",\"Args\":[\"${CertifID}\",\"${TransID}\",\"${TimeStamp}\",\"${KindOfTrans}\",\"${DeclarantID}\",\"${Signature}\",\"${ProcessID}\",\"${CertifTime}\",\"${Conditions}\",\"${Documents}\"]}"
  peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic $PEER_DATA -c "{\"function\":\"UpdateAsset\",\"Args\":[\"${ID}\",\"${Color}\",\"${Size}\",\"${Owner}\",\"${AppraisedValue}\"]}"
  res=$?
  set +x
  if [ $res -ne 0 ]; then
    errorln "Failed to UPDATING the Ledger...!"
    exit 1
  else
    successln "$ID UPDATING Done!"
  fi
}

# Updating the world state and the Ledger
function insertToLedger() {
  set -x
  # peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic $PEER_DATA -c "{\"function\":\"UpdateData\",\"Args\":[\"${CertifID}\",\"${TransID}\",\"${TimeStamp}\",\"${KindOfTrans}\",\"${DeclarantID}\",\"${Signature}\",\"${ProcessID}\",\"${CertifTime}\",\"${Conditions}\",\"${Documents}\"]}"
  peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic $PEER_DATA -c "{\"function\":\"CreateAsset\",\"Args\":[\"${ID}\",\"${Color}\",\"${Size}\",\"${Owner}\",\"${AppraisedValue}\"]}"
  res=$?
  set +x
  if [ $res -ne 0 ]; then
    errorln "Failed to UPDATING the Ledger...!"
    exit 1
  else
    successln "$ID UPDATING Done!"
  fi
}

# Query the world state and the Ledger
function queryData() {
  set -x
  peer chaincode query -C mychannel -n basic -c "{\"Args\":[\"GetAllAssets\",\"${ID}\"]}"
  res=$?
  set +x
  if [ $res -ne 0 ]; then
    errorln "Failed to QUERY the Ledger...!"
    exit 1
  else
    successln "$ID QUERY Done!"
  fi
}

# Deleting from the world state and updating the Ledger
function deleteData() {
  set -x
  peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic $PEER_DATA -c "{\"function\":\"DeleteAsset\",\"Args\":[\"${ID}\"]}"
  res=$?
  set +x
  if [ $res -ne 0 ]; then
    errorln "Failed to DELETE the Ledger...!"
    exit 1
  else
    successln "$ID DELETING Done!"
  fi
}

# Updating the world state and the Ledger
function clearLedger() {
  set -x
  # peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic $PEER_DATA -c '{"function":"ClearAllDatas","Args":[]}'
  peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic $PEER_DATA -c '{"function":"ClearAllAssets","Args":[]}'
  res=$?
  set +x
  if [ $res -ne 0 ]; then
    errorln "Failed to CLEAN the Ledger...!"
    exit 1
  else
    successln "CLEANING Done!"
  fi
}

## Parse mode 2
if [[ $# -lt 1 ]] ; then
  echo
  echo $'\e[0;31m'Need at least one argument!$'\e[0m'
  exit 1
fi

# parse the MODE
if [ "$#" -ge 1 -a "$#" -lt 8 ] ; then
  S_ORG=$1
  # parsePeerConnectionParameters ${OTHER_PEERS}
  export CORE_PEER_LOCALMSPID="Org${S_ORG}MSP"
  export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org${S_ORG}.example.com/peers/peer0.org${S_ORG}.example.com/tls/ca.crt
  export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org${S_ORG}.example.com/users/Admin@org${S_ORG}.example.com/msp
  S_ORG_P="$(expr $(expr $1 \* 2) + 5)051"
  export CORE_PEER_ADDRESS=localhost:$S_ORG_P

  PEER_DATA=""
  for i in $(seq 1 $NUM_ORG); do
    ORG_P="$(expr $(expr $i \* 2) + 5)051"
    ADD_P="${PWD}/organizations/peerOrganizations/org${i}.example.com/peers/peer0.org${i}.example.com/tls/ca.crt"
    PEER_DATA="$PEER_DATA --peerAddresses localhost:${ORG_P} --tlsRootCertFiles ${ADD_P}"
    # if [ "$i" != "$S_ORG" ]; then
    #   OTHER_PEERS="$OTHER_PEERS $i"
    # fi
  done

  MODE=$2
  case $MODE in
  init )
    ;;
  ledger )
    ;;
  clean )
    ;;
  query )
    ID=$3
    ;;
  delete )
    ID=$3
    ;;
  update )
    ID=$3
    Color=$4
    Size=$5
    Owner=$6
    AppraisedValue=$7
    ;;
  insert )
    ID=$3
    Color=$4
    Size=$5
    Owner=$6
    AppraisedValue=$7
    ;;
  * )
    errorln "Unknown flag: $MODE"
    exit 1
    ;;
  esac
else
  errorln "Wrong number of argument!"
  exit 1
fi


# Determine mode of operation and printing out what we asked for
if [ "$MODE" == "init" ] ; then
  echo
  echo "######## "$'\e[1;33m'Initializing the ASSETs ledger...$'\e[0m'" ########"
  echo
elif [ "$MODE" == "ledger" ] ; then
  echo
  echo "######## "$'\e[1;33m'Full Ledger...$'\e[0m'" ########"
  echo
elif [ "$MODE" == "update" ] ; then
  echo
  echo "######## "$'\e[1;33m'Updating the WORLD STATE of the ASSETs...$'\e[0m'" ########"
  echo
elif [ "$MODE" == "insert" ] ; then
  echo
  echo "######## "$'\e[1;33m'Adding new ASSET into the WORLD STATE of the ASSETs...$'\e[0m'" ########"
  echo
elif [ "$MODE" == "delete" ] ; then
  echo
  echo "######## "$'\e[1;33m'Delete DATA of the ASSETs from the WORLD STATE...$'\e[0m'" ########"
  echo
elif [ "$MODE" == "query" ] ; then
  echo
  echo "######## "$'\e[1;33m'Query DATA of the ASSETs from the WORLD STATE...$'\e[0m'" ########"
  echo
elif [ "$MODE" == "clean" ] ; then
  echo
  echo "######## "$'\e[1;33m'Clearing the WORLD STATE of all certifications...$'\e[0m'" ########"
  echo
else
  echo
  echo $'\e[0;31m'Wrong argument!$'\e[0m'
  exit 1
fi

if [ "${MODE}" == "init" ]; then
  initTheLedger
elif [ "${MODE}" == "update" ]; then
  updateLedger
elif [ "${MODE}" == "insert" ]; then
  insertToLedger
elif [ "${MODE}" == "ledger" ]; then
  queryLedgerAll
elif [ "${MODE}" == "query" ]; then
  queryData
elif [ "${MODE}" == "delete" ]; then
  deleteData
elif [ "${MODE}" == "clean" ]; then
  clearLedger
else
  echo
  echo $'\e[0;31m'Wrong argument!$'\e[0m'
  exit 1
fi
