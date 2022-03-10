#!/bin/sh

sudo apt update && sudo apt -y upgrade
sudo systemctl start docker && sudo systemctl enable docker && sudo usermod -a -G docker $(whoami)

cd OPtimal-ENdoresement-OPEN
curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.2.2 1.4.9

( cd OPtimal-ENdoresement-OPEN && ./Add8orgConf.sh )
( cd OPtimal-ENdoresement-OPEN/HF && chmod 777 installPeerAndConfiguration.sh && sudo ./installPeerAndConfiguration.sh 2.2.2 1.4.9 )
export PATH=$(pwd)/OPtimal-ENdoresement-OPEN/HF/bin:$PATH

( cd OPtimal-ENdoresement-OPEN/HF && rm -rf asset-transfer-abac/ asset-transfer-events/ asset-transfer-ledger-queries/ )
( cd OPtimal-ENdoresement-OPEN/HF && rm -rf asset-transfer-private-data/ asset-transfer-sbe/ asset-transfer-secured-agreement/ )
( cd OPtimal-ENdoresement-OPEN/HF && rm -rf auction/ chaincode/ commercial-paper/ fabcar/ high-throughput/ off_chain_data/ )
( cd OPtimal-ENdoresement-OPEN/HF && rm -rf token-utxo/ token-erc-20/ ci/ interest_rate_swaps/ )
