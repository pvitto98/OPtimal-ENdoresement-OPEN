#!/bin/sh

sudo apt update && sudo apt -y upgrade
sudo systemctl start docker && sudo systemctl enable docker && sudo usermod -a -G docker $(whoami)

curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.2.2 1.4.9

export PATH=$(pwd)/OPtimal-ENdoresement-OPEN/fabric-samples/bin:$PATH

( cd fabric-samples && rm -rf asset-transfer-abac/ asset-transfer-events/ asset-transfer-ledger-queries/ )
( cd fabric-samples && rm -rf asset-transfer-private-data/ asset-transfer-sbe/ asset-transfer-secured-agreement/ )
( cd fabric-samples && rm -rf auction/ chaincode/ commercial-paper/ fabcar/ high-throughput/ off_chain_data/ )
( cd fabric-samples && rm -rf token-utxo/ token-erc-20/ ci/ interest_rate_swaps/ )
