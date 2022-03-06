#!/bin/bash

function createOrg1() {
  infoln "Enrolling the CA admin"
  mkdir -p organizations/peerOrganizations/org1.example.com/

  export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/peerOrganizations/org1.example.com/

  infoln "${PWD}"
  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:7054 --caname ca-org1 --tls.certfiles ${PWD}/organizations/fabric-ca/org1/tls-cert.pem
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-7054-ca-org1.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-7054-ca-org1.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-7054-ca-org1.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-7054-ca-org1.pem
    OrganizationalUnitIdentifier: orderer' >${PWD}/organizations/peerOrganizations/org1.example.com/msp/config.yaml

  infoln "Registering peer0"
  set -x
  fabric-ca-client register --caname ca-org1 --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org1/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org1 --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org1/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org1 --id.name org1admin --id.secret org1adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org1/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:7054 --caname ca-org1 -M ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/msp --csr.hosts peer0.org1.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org1/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org1.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/msp/config.yaml

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:7054 --caname ca-org1 -M ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls --enrollment.profile tls --csr.hosts peer0.org1.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org1/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
  cp ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/signcerts/* ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/server.crt
  cp ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/keystore/* ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/server.key

  mkdir -p ${PWD}/organizations/peerOrganizations/org1.example.com/msp/tlscacerts
  cp ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org1.example.com/msp/tlscacerts/ca.crt

  mkdir -p ${PWD}/organizations/peerOrganizations/org1.example.com/tlsca
  cp ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org1.example.com/tlsca/tlsca.org1.example.com-cert.pem

  mkdir -p ${PWD}/organizations/peerOrganizations/org1.example.com/ca
  cp ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/msp/cacerts/* ${PWD}/organizations/peerOrganizations/org1.example.com/ca/ca.org1.example.com-cert.pem

  infoln "Generating the user msp"
  set -x
  fabric-ca-client enroll -u https://user1:user1pw@localhost:7054 --caname ca-org1 -M ${PWD}/organizations/peerOrganizations/org1.example.com/users/User1@org1.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org1/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org1.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org1.example.com/users/User1@org1.example.com/msp/config.yaml

  infoln "Generating the org admin msp"
  set -x
  fabric-ca-client enroll -u https://org1admin:org1adminpw@localhost:7054 --caname ca-org1 -M ${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org1/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org1.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp/config.yaml
}

function createOrg2() {
  infoln "Enrolling the CA admin"
  mkdir -p organizations/peerOrganizations/org2.example.com/

  export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/peerOrganizations/org2.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:8054 --caname ca-org2 --tls.certfiles ${PWD}/organizations/fabric-ca/org2/tls-cert.pem
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-8054-ca-org2.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-8054-ca-org2.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-8054-ca-org2.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-8054-ca-org2.pem
    OrganizationalUnitIdentifier: orderer' >${PWD}/organizations/peerOrganizations/org2.example.com/msp/config.yaml

  infoln "Registering peer0"
  set -x
  fabric-ca-client register --caname ca-org2 --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org2/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org2 --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org2/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org2 --id.name org2admin --id.secret org2adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org2/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:8054 --caname ca-org2 -M ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/msp --csr.hosts peer0.org2.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org2/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org2.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/msp/config.yaml

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:8054 --caname ca-org2 -M ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls --enrollment.profile tls --csr.hosts peer0.org2.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org2/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt
  cp ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/signcerts/* ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/server.crt
  cp ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/keystore/* ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/server.key

  mkdir -p ${PWD}/organizations/peerOrganizations/org2.example.com/msp/tlscacerts
  cp ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org2.example.com/msp/tlscacerts/ca.crt

  mkdir -p ${PWD}/organizations/peerOrganizations/org2.example.com/tlsca
  cp ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org2.example.com/tlsca/tlsca.org2.example.com-cert.pem

  mkdir -p ${PWD}/organizations/peerOrganizations/org2.example.com/ca
  cp ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/msp/cacerts/* ${PWD}/organizations/peerOrganizations/org2.example.com/ca/ca.org2.example.com-cert.pem

  infoln "Generating the user msp"
  set -x
  fabric-ca-client enroll -u https://user1:user1pw@localhost:8054 --caname ca-org2 -M ${PWD}/organizations/peerOrganizations/org2.example.com/users/User1@org2.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org2/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org2.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org2.example.com/users/User1@org2.example.com/msp/config.yaml

  infoln "Generating the org admin msp"
  set -x
  fabric-ca-client enroll -u https://org2admin:org2adminpw@localhost:8054 --caname ca-org2 -M ${PWD}/organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org2/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org2.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp/config.yaml
}

function createOrg3() {
  infoln "Enrolling the CA admin"
  mkdir -p organizations/peerOrganizations/org3.example.com/
  infoln "1"
  export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/peerOrganizations/org3.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:11054 --caname ca-org3 --tls.certfiles ${PWD}/organizations/fabric-ca/org3/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "${PWD}"

  infoln "2"

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-11054-ca-org3.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-11054-ca-org3.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-11054-ca-org3.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-11054-ca-org3.pem
    OrganizationalUnitIdentifier: orderer' >${PWD}/organizations/peerOrganizations/org3.example.com/msp/config.yaml

    infoln "3"

  infoln "Registering peer0"
  set -x
  fabric-ca-client register --caname ca-org3 --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org3/tls-cert.pem
  { set +x; } 2>/dev/null
  infoln "4"

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org3 --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org3/tls-cert.pem
  { set +x; } 2>/dev/null
  infoln "5"

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org3 --id.name org3admin --id.secret org3adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org3/tls-cert.pem
  { set +x; } 2>/dev/null
  infoln "6"

  infoln "Generating the peer0 msp"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:11054 --caname ca-org3 -M ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/msp --csr.hosts peer0.org3.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org3/tls-cert.pem
  { set +x; } 2>/dev/null
  infoln "7"

  cp ${PWD}/organizations/peerOrganizations/org3.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/msp/config.yaml
  infoln "8"

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:11054 --caname ca-org3 -M ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls --enrollment.profile tls --csr.hosts peer0.org3.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org3/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/ca.crt
  cp ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/signcerts/* ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/server.crt
  cp ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/keystore/* ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/server.key

  mkdir -p ${PWD}/organizations/peerOrganizations/org3.example.com/msp/tlscacerts
  cp ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org3.example.com/msp/tlscacerts/ca.crt

  mkdir -p ${PWD}/organizations/peerOrganizations/org3.example.com/tlsca
  cp ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org3.example.com/tlsca/tlsca.org3.example.com-cert.pem

  mkdir -p ${PWD}/organizations/peerOrganizations/org3.example.com/ca
  cp ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/msp/cacerts/* ${PWD}/organizations/peerOrganizations/org3.example.com/ca/ca.org3.example.com-cert.pem

  infoln "Generating the user msp"
  set -x
  fabric-ca-client enroll -u https://user1:user1pw@localhost:11054 --caname ca-org3 -M ${PWD}/organizations/peerOrganizations/org3.example.com/users/User1@org3.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org3/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org3.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org3.example.com/users/User1@org3.example.com/msp/config.yaml

  infoln "Generating the org admin msp"
  set -x
  fabric-ca-client enroll -u https://org3admin:org3adminpw@localhost:11054 --caname ca-org3 -M ${PWD}/organizations/peerOrganizations/org3.example.com/users/Admin@org3.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org3/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org3.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org3.example.com/users/Admin@org3.example.com/msp/config.yaml
}

function createOrg4() {
  infoln "Enrolling the CA admin"
  mkdir -p organizations/peerOrganizations/org4.example.com/

  export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/peerOrganizations/org4.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:13054 --caname ca-org4 --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-13054-ca-org4.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-13054-ca-org4.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-13054-ca-org4.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-13054-ca-org4.pem
    OrganizationalUnitIdentifier: orderer' >${PWD}/organizations/peerOrganizations/org4.example.com/msp/config.yaml

  infoln "Registering peer0"
  set -x
  fabric-ca-client register --caname ca-org4 --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org4 --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org4 --id.name org4admin --id.secret org4adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:13054 --caname ca-org4 -M ${PWD}/organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/msp --csr.hosts peer0.org4.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org4.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/msp/config.yaml

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:13054 --caname ca-org4 -M ${PWD}/organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls --enrollment.profile tls --csr.hosts peer0.org4.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/ca.crt
  cp ${PWD}/organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/signcerts/* ${PWD}/organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/server.crt
  cp ${PWD}/organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/keystore/* ${PWD}/organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/server.key

  mkdir -p ${PWD}/organizations/peerOrganizations/org4.example.com/msp/tlscacerts
  cp ${PWD}/organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org4.example.com/msp/tlscacerts/ca.crt

  mkdir -p ${PWD}/organizations/peerOrganizations/org4.example.com/tlsca
  cp ${PWD}/organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org4.example.com/tlsca/tlsca.org4.example.com-cert.pem

  mkdir -p ${PWD}/organizations/peerOrganizations/org4.example.com/ca
  cp ${PWD}/organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/msp/cacerts/* ${PWD}/organizations/peerOrganizations/org4.example.com/ca/ca.org4.example.com-cert.pem

  infoln "Generating the user msp"
  set -x
  fabric-ca-client enroll -u https://user1:user1pw@localhost:13054 --caname ca-org4 -M ${PWD}/organizations/peerOrganizations/org4.example.com/users/User1@org4.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org4.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org4.example.com/users/User1@org4.example.com/msp/config.yaml

  infoln "Generating the org admin msp"
  set -x
  fabric-ca-client enroll -u https://org4admin:org4adminpw@localhost:13054 --caname ca-org4 -M ${PWD}/organizations/peerOrganizations/org4.example.com/users/Admin@org4.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org4.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org4.example.com/users/Admin@org4.example.com/msp/config.yaml
}

function createOrg5() {

  mkdir -p organizations/peerOrganizations/org5.example.com/

  export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/peerOrganizations/org5.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:15054 --caname ca-org5 --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-15054-ca-org5.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-15054-ca-org5.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-15054-ca-org5.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-15054-ca-org5.pem
    OrganizationalUnitIdentifier: orderer' >${PWD}/organizations/peerOrganizations/org5.example.com/msp/config.yaml

  infoln "Registering peer0"
  set -x
  fabric-ca-client register --caname ca-org5 --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org5 --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org5 --id.name org5admin --id.secret org5adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:15054 --caname ca-org5 -M ${PWD}/organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/msp --csr.hosts peer0.org5.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org5.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/msp/config.yaml

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:15054 --caname ca-org5 -M ${PWD}/organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls --enrollment.profile tls --csr.hosts peer0.org5.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/ca.crt
  cp ${PWD}/organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/signcerts/* ${PWD}/organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/server.crt
  cp ${PWD}/organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/keystore/* ${PWD}/organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/server.key

  mkdir -p ${PWD}/organizations/peerOrganizations/org5.example.com/msp/tlscacerts
  cp ${PWD}/organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org5.example.com/msp/tlscacerts/ca.crt

  mkdir -p ${PWD}/organizations/peerOrganizations/org5.example.com/tlsca
  cp ${PWD}/organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org5.example.com/tlsca/tlsca.org5.example.com-cert.pem

  mkdir -p ${PWD}/organizations/peerOrganizations/org5.example.com/ca
  cp ${PWD}/organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/msp/cacerts/* ${PWD}/organizations/peerOrganizations/org5.example.com/ca/ca.org5.example.com-cert.pem

  infoln "Generating the user msp"
  set -x
  fabric-ca-client enroll -u https://user1:user1pw@localhost:15054 --caname ca-org5 -M ${PWD}/organizations/peerOrganizations/org5.example.com/users/User1@org5.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org5.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org5.example.com/users/User1@org5.example.com/msp/config.yaml

  infoln "Generating the org admin msp"
  set -x
  fabric-ca-client enroll -u https://org5admin:org5adminpw@localhost:15054 --caname ca-org5 -M ${PWD}/organizations/peerOrganizations/org5.example.com/users/Admin@org5.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org5.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org5.example.com/users/Admin@org5.example.com/msp/config.yaml
}

function createOrg6() {
  infoln "Enrolling the CA admin"
  mkdir -p organizations/peerOrganizations/org6.example.com/

  export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/peerOrganizations/org6.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:17054 --caname ca-org6 --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-17054-ca-org6.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-17054-ca-org6.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-17054-ca-org6.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-17054-ca-org6.pem
    OrganizationalUnitIdentifier: orderer' >${PWD}/organizations/peerOrganizations/org6.example.com/msp/config.yaml

  infoln "Registering peer0"
  set -x
  fabric-ca-client register --caname ca-org6 --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org6 --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org6 --id.name org6admin --id.secret org6adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:17054 --caname ca-org6 -M ${PWD}/organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/msp --csr.hosts peer0.org6.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org6.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/msp/config.yaml

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:17054 --caname ca-org6 -M ${PWD}/organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls --enrollment.profile tls --csr.hosts peer0.org6.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/ca.crt
  cp ${PWD}/organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/signcerts/* ${PWD}/organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/server.crt
  cp ${PWD}/organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/keystore/* ${PWD}/organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/server.key

  mkdir -p ${PWD}/organizations/peerOrganizations/org6.example.com/msp/tlscacerts
  cp ${PWD}/organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org6.example.com/msp/tlscacerts/ca.crt

  mkdir -p ${PWD}/organizations/peerOrganizations/org6.example.com/tlsca
  cp ${PWD}/organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org6.example.com/tlsca/tlsca.org6.example.com-cert.pem

  mkdir -p ${PWD}/organizations/peerOrganizations/org6.example.com/ca
  cp ${PWD}/organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/msp/cacerts/* ${PWD}/organizations/peerOrganizations/org6.example.com/ca/ca.org6.example.com-cert.pem

  infoln "Generating the user msp"
  set -x
  fabric-ca-client enroll -u https://user1:user1pw@localhost:17054 --caname ca-org6 -M ${PWD}/organizations/peerOrganizations/org6.example.com/users/User1@org6.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org6.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org6.example.com/users/User1@org6.example.com/msp/config.yaml

  infoln "Generating the org admin msp"
  set -x
  fabric-ca-client enroll -u https://org6admin:org6adminpw@localhost:17054 --caname ca-org6 -M ${PWD}/organizations/peerOrganizations/org6.example.com/users/Admin@org6.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org6.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org6.example.com/users/Admin@org6.example.com/msp/config.yaml
}

function createOrg7() {
  infoln "Enrolling the CA admin"
  mkdir -p organizations/peerOrganizations/org7.example.com/

  export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/peerOrganizations/org7.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:19054 --caname ca-org7 --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-19054-ca-org7.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-19054-ca-org7.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-19054-ca-org7.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-19054-ca-org7.pem
    OrganizationalUnitIdentifier: orderer' >${PWD}/organizations/peerOrganizations/org7.example.com/msp/config.yaml

  infoln "Registering peer0"
  set -x
  fabric-ca-client register --caname ca-org7 --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org7 --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org7 --id.name org7admin --id.secret org7adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:19054 --caname ca-org7 -M ${PWD}/organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/msp --csr.hosts peer0.org7.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org7.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/msp/config.yaml

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:19054 --caname ca-org7 -M ${PWD}/organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls --enrollment.profile tls --csr.hosts peer0.org7.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/ca.crt
  cp ${PWD}/organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/signcerts/* ${PWD}/organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/server.crt
  cp ${PWD}/organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/keystore/* ${PWD}/organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/server.key

  mkdir -p ${PWD}/organizations/peerOrganizations/org7.example.com/msp/tlscacerts
  cp ${PWD}/organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org7.example.com/msp/tlscacerts/ca.crt

  mkdir -p ${PWD}/organizations/peerOrganizations/org7.example.com/tlsca
  cp ${PWD}/organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org7.example.com/tlsca/tlsca.org7.example.com-cert.pem

  mkdir -p ${PWD}/organizations/peerOrganizations/org7.example.com/ca
  cp ${PWD}/organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/msp/cacerts/* ${PWD}/organizations/peerOrganizations/org7.example.com/ca/ca.org7.example.com-cert.pem

  infoln "Generating the user msp"
  set -x
  fabric-ca-client enroll -u https://user1:user1pw@localhost:19054 --caname ca-org7 -M ${PWD}/organizations/peerOrganizations/org7.example.com/users/User1@org7.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org7.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org7.example.com/users/User1@org7.example.com/msp/config.yaml

  infoln "Generating the org admin msp"
  set -x
  fabric-ca-client enroll -u https://org7admin:org7adminpw@localhost:19054 --caname ca-org7 -M ${PWD}/organizations/peerOrganizations/org7.example.com/users/Admin@org7.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org7.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org7.example.com/users/Admin@org7.example.com/msp/config.yaml
}

function createOrg8() {
  infoln "Enrolling the CA admin"
  mkdir -p organizations/peerOrganizations/org8.example.com/

  export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/peerOrganizations/org8.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:21054 --caname ca-org8 --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-21054-ca-org8.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-21054-ca-org8.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-21054-ca-org8.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-21054-ca-org8.pem
    OrganizationalUnitIdentifier: orderer' >${PWD}/organizations/peerOrganizations/org8.example.com/msp/config.yaml

  infoln "Registering peer0"
  set -x
  fabric-ca-client register --caname ca-org8 --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org8 --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org8 --id.name org8admin --id.secret org8adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:21054 --caname ca-org8 -M ${PWD}/organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/msp --csr.hosts peer0.org8.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org8.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/msp/config.yaml

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:21054 --caname ca-org8 -M ${PWD}/organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls --enrollment.profile tls --csr.hosts peer0.org8.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/ca.crt
  cp ${PWD}/organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/signcerts/* ${PWD}/organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/server.crt
  cp ${PWD}/organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/keystore/* ${PWD}/organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/server.key

  mkdir -p ${PWD}/organizations/peerOrganizations/org8.example.com/msp/tlscacerts
  cp ${PWD}/organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org8.example.com/msp/tlscacerts/ca.crt

  mkdir -p ${PWD}/organizations/peerOrganizations/org8.example.com/tlsca
  cp ${PWD}/organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org8.example.com/tlsca/tlsca.org8.example.com-cert.pem

  mkdir -p ${PWD}/organizations/peerOrganizations/org8.example.com/ca
  cp ${PWD}/organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/msp/cacerts/* ${PWD}/organizations/peerOrganizations/org8.example.com/ca/ca.org8.example.com-cert.pem

  infoln "Generating the user msp"
  set -x
  fabric-ca-client enroll -u https://user1:user1pw@localhost:21054 --caname ca-org8 -M ${PWD}/organizations/peerOrganizations/org8.example.com/users/User1@org8.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org8.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org8.example.com/users/User1@org8.example.com/msp/config.yaml

  infoln "Generating the org admin msp"
  set -x
  fabric-ca-client enroll -u https://org8admin:org8adminpw@localhost:21054 --caname ca-org8 -M ${PWD}/organizations/peerOrganizations/org8.example.com/users/Admin@org8.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/peerOrganizations/org8.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org8.example.com/users/Admin@org8.example.com/msp/config.yaml
}


#######OLD
function createOrg4_old() {
	infoln "Enrolling the CA admin"
	mkdir -p ../organizations/peerOrganizations/org4.example.com/

	export FABRIC_CA_CLIENT_HOME=${PWD}/../organizations/peerOrganizations/org4.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:13054 --caname ca-org4 --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-13054-ca-org4.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-13054-ca-org4.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-13054-ca-org4.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-13054-ca-org4.pem
    OrganizationalUnitIdentifier: orderer' > ${PWD}/../organizations/peerOrganizations/org4.example.com/msp/config.yaml

	infoln "Registering peer0"
  set -x
	fabric-ca-client register --caname ca-org4 --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org4 --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org4 --id.name org4admin --id.secret org4adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
	fabric-ca-client enroll -u https://peer0:peer0pw@localhost:13054 --caname ca-org4 -M ${PWD}/../organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/msp --csr.hosts peer0.org4.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org4.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/msp/config.yaml

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:13054 --caname ca-org4 -M ${PWD}/../organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls --enrollment.profile tls --csr.hosts peer0.org4.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null


  cp ${PWD}/../organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/ca.crt
  cp ${PWD}/../organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/signcerts/* ${PWD}/../organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/server.crt
  cp ${PWD}/../organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/keystore/* ${PWD}/../organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/server.key

  mkdir ${PWD}/../organizations/peerOrganizations/org4.example.com/msp/tlscacerts
  cp ${PWD}/../organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org4.example.com/msp/tlscacerts/ca.crt

  mkdir ${PWD}/../organizations/peerOrganizations/org4.example.com/tlsca
  cp ${PWD}/../organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org4.example.com/tlsca/tlsca.org4.example.com-cert.pem

  mkdir ${PWD}/../organizations/peerOrganizations/org4.example.com/ca
  cp ${PWD}/../organizations/peerOrganizations/org4.example.com/peers/peer0.org4.example.com/msp/cacerts/* ${PWD}/../organizations/peerOrganizations/org4.example.com/ca/ca.org4.example.com-cert.pem

  infoln "Generating the user msp"
  set -x
	fabric-ca-client enroll -u https://user1:user1pw@localhost:13054 --caname ca-org4 -M ${PWD}/../organizations/peerOrganizations/org4.example.com/users/User1@org4.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org4.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org4.example.com/users/User1@org4.example.com/msp/config.yaml

  infoln "Generating the org admin msp"
  set -x
	fabric-ca-client enroll -u https://org4admin:org4adminpw@localhost:13054 --caname ca-org4 -M ${PWD}/../organizations/peerOrganizations/org4.example.com/users/Admin@org4.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org4/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org4.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org4.example.com/users/Admin@org4.example.com/msp/config.yaml
}


function createOrg5_old() {
	infoln "Enrolling the CA admin"
	mkdir -p ../organizations/peerOrganizations/org5.example.com/

	export FABRIC_CA_CLIENT_HOME=${PWD}/../organizations/peerOrganizations/org5.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:15054 --caname ca-org5 --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-15054-ca-org5.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-15054-ca-org5.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-15054-ca-org5.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-15054-ca-org5.pem
    OrganizationalUnitIdentifier: orderer' > ${PWD}/../organizations/peerOrganizations/org5.example.com/msp/config.yaml

	infoln "Registering peer0"
  set -x
	fabric-ca-client register --caname ca-org5 --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org5 --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org5 --id.name org5admin --id.secret org5adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
	fabric-ca-client enroll -u https://peer0:peer0pw@localhost:15054 --caname ca-org5 -M ${PWD}/../organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/msp --csr.hosts peer0.org5.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org5.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/msp/config.yaml

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:15054 --caname ca-org5 -M ${PWD}/../organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls --enrollment.profile tls --csr.hosts peer0.org5.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null


  cp ${PWD}/../organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/ca.crt
  cp ${PWD}/../organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/signcerts/* ${PWD}/../organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/server.crt
  cp ${PWD}/../organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/keystore/* ${PWD}/../organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/server.key

  mkdir ${PWD}/../organizations/peerOrganizations/org5.example.com/msp/tlscacerts
  cp ${PWD}/../organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org5.example.com/msp/tlscacerts/ca.crt

  mkdir ${PWD}/../organizations/peerOrganizations/org5.example.com/tlsca
  cp ${PWD}/../organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org5.example.com/tlsca/tlsca.org5.example.com-cert.pem

  mkdir ${PWD}/../organizations/peerOrganizations/org5.example.com/ca
  cp ${PWD}/../organizations/peerOrganizations/org5.example.com/peers/peer0.org5.example.com/msp/cacerts/* ${PWD}/../organizations/peerOrganizations/org5.example.com/ca/ca.org5.example.com-cert.pem

  infoln "Generating the user msp"
  set -x
	fabric-ca-client enroll -u https://user1:user1pw@localhost:15054 --caname ca-org5 -M ${PWD}/../organizations/peerOrganizations/org5.example.com/users/User1@org5.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org5.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org5.example.com/users/User1@org5.example.com/msp/config.yaml

  infoln "Generating the org admin msp"
  set -x
	fabric-ca-client enroll -u https://org5admin:org5adminpw@localhost:15054 --caname ca-org5 -M ${PWD}/../organizations/peerOrganizations/org5.example.com/users/Admin@org5.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org5/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org5.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org5.example.com/users/Admin@org5.example.com/msp/config.yaml
}


function createOrg6_old() {
	infoln "Enrolling the CA admin"
	mkdir -p ../organizations/peerOrganizations/org6.example.com/

	export FABRIC_CA_CLIENT_HOME=${PWD}/../organizations/peerOrganizations/org6.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:17054 --caname ca-org6 --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-17054-ca-org6.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-17054-ca-org6.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-17054-ca-org6.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-17054-ca-org6.pem
    OrganizationalUnitIdentifier: orderer' > ${PWD}/../organizations/peerOrganizations/org6.example.com/msp/config.yaml

	infoln "Registering peer0"
  set -x
	fabric-ca-client register --caname ca-org6 --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org6 --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org6 --id.name org6admin --id.secret org6adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
	fabric-ca-client enroll -u https://peer0:peer0pw@localhost:17054 --caname ca-org6 -M ${PWD}/../organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/msp --csr.hosts peer0.org6.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org6.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/msp/config.yaml

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:17054 --caname ca-org6 -M ${PWD}/../organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls --enrollment.profile tls --csr.hosts peer0.org6.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null


  cp ${PWD}/../organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/ca.crt
  cp ${PWD}/../organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/signcerts/* ${PWD}/../organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/server.crt
  cp ${PWD}/../organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/keystore/* ${PWD}/../organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/server.key

  mkdir ${PWD}/../organizations/peerOrganizations/org6.example.com/msp/tlscacerts
  cp ${PWD}/../organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org6.example.com/msp/tlscacerts/ca.crt

  mkdir ${PWD}/../organizations/peerOrganizations/org6.example.com/tlsca
  cp ${PWD}/../organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org6.example.com/tlsca/tlsca.org6.example.com-cert.pem

  mkdir ${PWD}/../organizations/peerOrganizations/org6.example.com/ca
  cp ${PWD}/../organizations/peerOrganizations/org6.example.com/peers/peer0.org6.example.com/msp/cacerts/* ${PWD}/../organizations/peerOrganizations/org6.example.com/ca/ca.org6.example.com-cert.pem

  infoln "Generating the user msp"
  set -x
	fabric-ca-client enroll -u https://user1:user1pw@localhost:17054 --caname ca-org6 -M ${PWD}/../organizations/peerOrganizations/org6.example.com/users/User1@org6.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org6.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org6.example.com/users/User1@org6.example.com/msp/config.yaml

  infoln "Generating the org admin msp"
  set -x
	fabric-ca-client enroll -u https://org6admin:org6adminpw@localhost:17054 --caname ca-org6 -M ${PWD}/../organizations/peerOrganizations/org6.example.com/users/Admin@org6.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org6/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org6.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org6.example.com/users/Admin@org6.example.com/msp/config.yaml
}


function createOrg7_old() {
	infoln "Enrolling the CA admin"
	mkdir -p ../organizations/peerOrganizations/org7.example.com/

	export FABRIC_CA_CLIENT_HOME=${PWD}/../organizations/peerOrganizations/org7.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:19054 --caname ca-org7 --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-19054-ca-org7.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-19054-ca-org7.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-19054-ca-org7.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-19054-ca-org7.pem
    OrganizationalUnitIdentifier: orderer' > ${PWD}/../organizations/peerOrganizations/org7.example.com/msp/config.yaml

	infoln "Registering peer0"
  set -x
	fabric-ca-client register --caname ca-org7 --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org7 --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org7 --id.name org7admin --id.secret org7adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
	fabric-ca-client enroll -u https://peer0:peer0pw@localhost:19054 --caname ca-org7 -M ${PWD}/../organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/msp --csr.hosts peer0.org7.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org7.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/msp/config.yaml

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:19054 --caname ca-org7 -M ${PWD}/../organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls --enrollment.profile tls --csr.hosts peer0.org7.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null


  cp ${PWD}/../organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/ca.crt
  cp ${PWD}/../organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/signcerts/* ${PWD}/../organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/server.crt
  cp ${PWD}/../organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/keystore/* ${PWD}/../organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/server.key

  mkdir ${PWD}/../organizations/peerOrganizations/org7.example.com/msp/tlscacerts
  cp ${PWD}/../organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org7.example.com/msp/tlscacerts/ca.crt

  mkdir ${PWD}/../organizations/peerOrganizations/org7.example.com/tlsca
  cp ${PWD}/../organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org7.example.com/tlsca/tlsca.org7.example.com-cert.pem

  mkdir ${PWD}/../organizations/peerOrganizations/org7.example.com/ca
  cp ${PWD}/../organizations/peerOrganizations/org7.example.com/peers/peer0.org7.example.com/msp/cacerts/* ${PWD}/../organizations/peerOrganizations/org7.example.com/ca/ca.org7.example.com-cert.pem

  infoln "Generating the user msp"
  set -x
	fabric-ca-client enroll -u https://user1:user1pw@localhost:19054 --caname ca-org7 -M ${PWD}/../organizations/peerOrganizations/org7.example.com/users/User1@org7.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org7.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org7.example.com/users/User1@org7.example.com/msp/config.yaml

  infoln "Generating the org admin msp"
  set -x
	fabric-ca-client enroll -u https://org7admin:org7adminpw@localhost:19054 --caname ca-org7 -M ${PWD}/../organizations/peerOrganizations/org7.example.com/users/Admin@org7.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org7/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org7.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org7.example.com/users/Admin@org7.example.com/msp/config.yaml
}


function createOrg8_old() {
	infoln "Enrolling the CA admin"
	mkdir -p ../organizations/peerOrganizations/org8.example.com/

	export FABRIC_CA_CLIENT_HOME=${PWD}/../organizations/peerOrganizations/org8.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:21054 --caname ca-org8 --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-21054-ca-org8.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-21054-ca-org8.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-21054-ca-org8.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-21054-ca-org8.pem
    OrganizationalUnitIdentifier: orderer' > ${PWD}/../organizations/peerOrganizations/org8.example.com/msp/config.yaml

	infoln "Registering peer0"
  set -x
	fabric-ca-client register --caname ca-org8 --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org8 --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org8 --id.name org8admin --id.secret org8adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
	fabric-ca-client enroll -u https://peer0:peer0pw@localhost:21054 --caname ca-org8 -M ${PWD}/../organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/msp --csr.hosts peer0.org8.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org8.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/msp/config.yaml

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:21054 --caname ca-org8 -M ${PWD}/../organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls --enrollment.profile tls --csr.hosts peer0.org8.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null


  cp ${PWD}/../organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/ca.crt
  cp ${PWD}/../organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/signcerts/* ${PWD}/../organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/server.crt
  cp ${PWD}/../organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/keystore/* ${PWD}/../organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/server.key

  mkdir ${PWD}/../organizations/peerOrganizations/org8.example.com/msp/tlscacerts
  cp ${PWD}/../organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org8.example.com/msp/tlscacerts/ca.crt

  mkdir ${PWD}/../organizations/peerOrganizations/org8.example.com/tlsca
  cp ${PWD}/../organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/tls/tlscacerts/* ${PWD}/../organizations/peerOrganizations/org8.example.com/tlsca/tlsca.org8.example.com-cert.pem

  mkdir ${PWD}/../organizations/peerOrganizations/org8.example.com/ca
  cp ${PWD}/../organizations/peerOrganizations/org8.example.com/peers/peer0.org8.example.com/msp/cacerts/* ${PWD}/../organizations/peerOrganizations/org8.example.com/ca/ca.org8.example.com-cert.pem

  infoln "Generating the user msp"
  set -x
	fabric-ca-client enroll -u https://user1:user1pw@localhost:21054 --caname ca-org8 -M ${PWD}/../organizations/peerOrganizations/org8.example.com/users/User1@org8.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org8.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org8.example.com/users/User1@org8.example.com/msp/config.yaml

  infoln "Generating the org admin msp"
  set -x
	fabric-ca-client enroll -u https://org8admin:org8adminpw@localhost:21054 --caname ca-org8 -M ${PWD}/../organizations/peerOrganizations/org8.example.com/users/Admin@org8.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org8/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/../organizations/peerOrganizations/org8.example.com/msp/config.yaml ${PWD}/../organizations/peerOrganizations/org8.example.com/users/Admin@org8.example.com/msp/config.yaml
}

function customCreateAllOrgs() {

  infoln "Creating all the orgs...."
  NUM_ORG=8

  for i in $(seq 4 $NUM_ORG); do

    ORG_P="$(expr $(expr $i \* 2) + 5)054"

    mkdir -p organizations/peerOrganizations/org${i}.example.com/


    infoln "Enrolling the CA admin for client${i}"

    export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/peerOrganizations/org${i}.example.com/

    set -x
    fabric-ca-client enroll -u https://admin:adminpw@localhost:${ORG_P} --caname ca-org${i} --tls.certfiles ${PWD}/organizations/fabric-ca/org${i}/tls-cert.pem
    { set +x; } 2>/dev/null

    echo "NodeOUs:
    Enable: true
    ClientOUIdentifier:
      Certificate: cacerts/localhost-${ORG_P}-ca-org${i}.pem
      OrganizationalUnitIdentifier: client
    PeerOUIdentifier:
      Certificate: cacerts/localhost-${ORG_P}-ca-org${i}.pem
      OrganizationalUnitIdentifier: peer
    AdminOUIdentifier:
      Certificate: cacerts/localhost-${ORG_P}-ca-org${i}.pem
      OrganizationalUnitIdentifier: admin
    OrdererOUIdentifier:
      Certificate: cacerts/localhost-${ORG_P}-ca-org${i}.pem
      OrganizationalUnitIdentifier: orderer"

      echo "NodeOUs:
      Enable: true
      ClientOUIdentifier:
        Certificate: cacerts/localhost-${ORG_P}-ca-org${i}.pem
        OrganizationalUnitIdentifier: client
      PeerOUIdentifier:
        Certificate: cacerts/localhost-${ORG_P}-ca-org${i}.pem
        OrganizationalUnitIdentifier: peer
      AdminOUIdentifier:
        Certificate: cacerts/localhost-${ORG_P}-ca-org${i}.pem
        OrganizationalUnitIdentifier: admin
      OrdererOUIdentifier:
        Certificate: cacerts/localhost-${ORG_P}-ca-org${i}.pem
        OrganizationalUnitIdentifier: orderer" >${PWD}/organizations/peerOrganizations/org${i}.example.com/msp/config.yaml

    infoln "Registering peer0"
    set -x
    fabric-ca-client register --caname ca-org${i} --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org${i}/tls-cert.pem
    { set +x; } 2>/dev/null

    infoln "Registering user"
    set -x
    fabric-ca-client register --caname ca-org${i} --id.name user1 --id.secret user1pw --id.type client --tls.certfiles ${PWD}/organizations/fabric-ca/org${i}/tls-cert.pem
    { set +x; } 2>/dev/null

    infoln "Registering the org admin"
    set -x
    fabric-ca-client register --caname ca-org${i} --id.name org${i}admin --id.secret org${i}adminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/org${i}/tls-cert.pem
    { set +x; } 2>/dev/null

    infoln "Generating the peer0 msp"
    set -x
    fabric-ca-client enroll -u https://peer0:peer0pw@localhost:${ORG_P} --caname ca-org${i} -M ${PWD}/organizations/peerOrganizations/org${i}.example.com/peers/peer0.org${i}.example.com/msp --csr.hosts peer0.org${i}.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org${i}/tls-cert.pem
    { set +x; } 2>/dev/null

    cp ${PWD}/organizations/peerOrganizations/org${i}.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org${i}.example.com/peers/peer0.org${i}.example.com/msp/config.yaml

    infoln "Generating the peer0-tls certificates"
    set -x
    fabric-ca-client enroll -u https://peer0:peer0pw@localhost:${ORG_P} --caname ca-org${i} -M ${PWD}/organizations/peerOrganizations/org${i}.example.com/peers/peer0.org${i}.example.com/tls --enrollment.profile tls --csr.hosts peer0.org${i}.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org${i}/tls-cert.pem
    { set +x; } 2>/dev/null

    cp ${PWD}/organizations/peerOrganizations/org${i}.example.com/peers/peer0.org${i}.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org${i}.example.com/peers/peer0.org${i}.example.com/tls/ca.crt
    cp ${PWD}/organizations/peerOrganizations/org${i}.example.com/peers/peer0.org${i}.example.com/tls/signcerts/* ${PWD}/organizations/peerOrganizations/org${i}.example.com/peers/peer0.org${i}.example.com/tls/server.crt
    cp ${PWD}/organizations/peerOrganizations/org${i}.example.com/peers/peer0.org${i}.example.com/tls/keystore/* ${PWD}/organizations/peerOrganizations/org${i}.example.com/peers/peer0.org${i}.example.com/tls/server.key

    mkdir -p ${PWD}/organizations/peerOrganizations/org${i}.example.com/msp/tlscacerts
    cp ${PWD}/organizations/peerOrganizations/org${i}.example.com/peers/peer0.org${i}.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org${i}.example.com/msp/tlscacerts/ca.crt

    mkdir -p ${PWD}/organizations/peerOrganizations/org${i}.example.com/tlsca
    cp ${PWD}/organizations/peerOrganizations/org${i}.example.com/peers/peer0.org${i}.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org${i}.example.com/tlsca/tlsca.org${i}.example.com-cert.pem

    mkdir -p ${PWD}/organizations/peerOrganizations/org${i}.example.com/ca
    cp ${PWD}/organizations/peerOrganizations/org${i}.example.com/peers/peer0.org${i}.example.com/msp/cacerts/* ${PWD}/organizations/peerOrganizations/org${i}.example.com/ca/ca.org${i}.example.com-cert.pem

    infoln "Generating the user msp"
    set -x
    fabric-ca-client enroll -u https://user1:user1pw@localhost:${ORG_P} --caname ca-org${i} -M ${PWD}/organizations/peerOrganizations/org${i}.example.com/users/User1@org${i}.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org${i}/tls-cert.pem
    { set +x; } 2>/dev/null

    cp ${PWD}/organizations/peerOrganizations/org${i}.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org${i}.example.com/users/User1@org${i}.example.com/msp/config.yaml

    infoln "Generating the org admin msp"
    set -x
    fabric-ca-client enroll -u https://org${i}admin:org${i}adminpw@localhost:${ORG_P} --caname ca-org${i} -M ${PWD}/organizations/peerOrganizations/org${i}.example.com/users/Admin@org${i}.example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/org${i}/tls-cert.pem
    { set +x; } 2>/dev/null

    cp ${PWD}/organizations/peerOrganizations/org${i}.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org${i}.example.com/users/Admin@org${i}.example.com/msp/config.yaml
  done

}


function createOrderer() {
  infoln "Enrolling the CA admin"
  mkdir -p organizations/ordererOrganizations/example.com

  export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/ordererOrganizations/example.com

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:9054 --caname ca-orderer --tls.certfiles ${PWD}/organizations/fabric-ca/ordererOrg/tls-cert.pem
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-9054-ca-orderer.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-9054-ca-orderer.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-9054-ca-orderer.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-9054-ca-orderer.pem
    OrganizationalUnitIdentifier: orderer' >${PWD}/organizations/ordererOrganizations/example.com/msp/config.yaml

  infoln "Registering orderer"
  set -x
  fabric-ca-client register --caname ca-orderer --id.name orderer --id.secret ordererpw --id.type orderer --tls.certfiles ${PWD}/organizations/fabric-ca/ordererOrg/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Registering the orderer admin"
  set -x
  fabric-ca-client register --caname ca-orderer --id.name ordererAdmin --id.secret ordererAdminpw --id.type admin --tls.certfiles ${PWD}/organizations/fabric-ca/ordererOrg/tls-cert.pem
  { set +x; } 2>/dev/null

  infoln "Generating the orderer msp"
  set -x
  fabric-ca-client enroll -u https://orderer:ordererpw@localhost:9054 --caname ca-orderer -M ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp --csr.hosts orderer.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/ordererOrg/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/ordererOrganizations/example.com/msp/config.yaml ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/config.yaml

  infoln "Generating the orderer-tls certificates"
  set -x
  fabric-ca-client enroll -u https://orderer:ordererpw@localhost:9054 --caname ca-orderer -M ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls --enrollment.profile tls --csr.hosts orderer.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/ordererOrg/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/tlscacerts/* ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt
  cp ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/signcerts/* ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/server.crt
  cp ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/keystore/* ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/server.key

  mkdir -p ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts
  cp ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/tlscacerts/* ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem

  mkdir -p ${PWD}/organizations/ordererOrganizations/example.com/msp/tlscacerts
  cp ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/tlscacerts/* ${PWD}/organizations/ordererOrganizations/example.com/msp/tlscacerts/tlsca.example.com-cert.pem

  infoln "Generating the admin msp"
  set -x
  fabric-ca-client enroll -u https://ordererAdmin:ordererAdminpw@localhost:9054 --caname ca-orderer -M ${PWD}/organizations/ordererOrganizations/example.com/users/Admin@example.com/msp --tls.certfiles ${PWD}/organizations/fabric-ca/ordererOrg/tls-cert.pem
  { set +x; } 2>/dev/null

  cp ${PWD}/organizations/ordererOrganizations/example.com/msp/config.yaml ${PWD}/organizations/ordererOrganizations/example.com/users/Admin@example.com/msp/config.yaml
}
