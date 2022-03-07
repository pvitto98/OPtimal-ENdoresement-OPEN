/*
 * Copyright IBM Corp. All Rights Reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

'use strict';

const { Gateway, Wallets } = require('fabric-network');
const FabricCAServices = require('fabric-ca-client');
const path = require('path');
const { buildCAClient, registerAndEnrollUser, enrollAdmin } = require('../../test-application/javascript/CAUtil.js');
const { buildCCPOrg1, buildWallet } = require('../../test-application/javascript/AppUtil.js');

const { performance } = require('perf_hooks');


const channelName = 'mychannel';
const chaincodeName = 'basic';
const mspOrg1 = 'Org1MSP';
//'E COSI' PERCH'E 'E UN CLIENT INSTALLTO NELL'ORGANIZZAZIONE1?
const walletPath = path.join(__dirname, 'wallet');
const org1UserId = 'appUser';

const NUMBER_OF_TRANSACTIONS = 10

const timestamp = performance.now()

function prettyJSONString(inputString) {
	return JSON.stringify(JSON.parse(inputString), null, 2);
}

// pre-requisites:
// - fabric-sample two organization test-network setup with two peers, ordering service,
//   and 2 certificate authorities
//         ===> from directory /fabric-samples/test-network
//         ./network.sh up createChannel -ca
// - Use any of the asset-transfer-basic chaincodes deployed on the channel "mychannel"
//   with the chaincode name of "basic". The following deploy command will package,
//   install, approve, and commit the javascript chaincode, all the actions it takes
//   to deploy a chaincode to a channel.
//         ===> from directory /fabric-samples/test-network
//         ./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript/ -ccl javascript
// - Be sure that node.js is installed
//         ===> from directory /fabric-samples/asset-transfer-basic/application-javascript
//         node -v
// - npm installed code dependencies
//         ===> from directory /fabric-samples/asset-transfer-basic/application-javascript
//         npm install
// - to run this test application
//         ===> from directory /fabric-samples/asset-transfer-basic/application-javascript
//         node app.js

// NOTE: If you see  kind an error like these:
/*
    2020-08-07T20:23:17.590Z - error: [DiscoveryService]: send[mychannel] - Channel:mychannel received discovery error:access denied
    ******** FAILED to run the application: Error: DiscoveryService: mychannel error: access denied

   OR

   Failed to register user : Error: fabric-ca request register failed with errors [[ { code: 20, message: 'Authentication failure' } ]]
   ******** FAILED to run the application: Error: Identity not found in wallet: appUser
*/
// Delete the /fabric-samples/asset-transfer-basic/application-javascript/wallet directory
// and retry this application.
//
// The certificate authority must have been restarted and the saved certificates for the
// admin and application user are not valid. Deleting the wallet store will force these to be reset
// with the new certificate authority.
//

/**
 *  A test application to show basic queries operations with any of the asset-transfer-basic chaincodes
 *   -- How to submit a transaction
 *   -- How to query and check the results
 *
 * To see the SDK workings, try setting the logging to show on the console before running
 *        export HFC_LOGGING='{"debug":"console"}'
 */


async function main() {
	try {

		// build an in memory object with the network configuration (also known as a connection profile)
		const ccp = buildCCPOrg1();

		//PROVA RIMUOVENDO CONFIGURAZIONE DI RETE

		// build an instance of the fabric ca services client based on
		// the information in the network configuration
		const caClient = buildCAClient(FabricCAServices, ccp, 'ca.org1.example.com');

		//console.log(ccp)

		// setup the wallet to hold the credentials of the application user
		const wallet = await buildWallet(Wallets, walletPath);

		// in a real application this would be done on an administrative flow, and only once
		await enrollAdmin(caClient, wallet, mspOrg1);


		// in a real application this would be done only when a new user was required to be added
		// and would be part of an administrative flow
	  await registerAndEnrollUser(caClient, wallet, mspOrg1, org1UserId, 'org1.department1');

		// Create a new gateway instance for interacting with the fabric network.
		// In a real application this would be done as the backend server session is setup for
		// a user that has been verified.
		const gateway = new Gateway();


		//console.log(ccp)

		try {
			// setup the gateway instance
			// The user will now be able to create connections to the fabric network and be able to
			// submit transactions and query. All transactions submitted by this gateway will be
			// signed by this user using the credentials stored in the wallet.
			await gateway.connect(ccp, {
				wallet,
				identity: org1UserId,
				discovery: { enabled: true, asLocalhost: true } // using asLocalhost as this gateway is using a fabric network deployed locally
			});

			// Build a network instance based on the channel where the smart contract is deployed
			const network = await gateway.getNetwork(channelName);

			//console.log(network)

			// Get the contract from the network.
			const contract = network.getContract(chaincodeName);

			const fs = require('fs')

			var startExperiment = performance.now()
			let sum = 0
			let count = 0
			let avg = 0
			let assetName


			for (let i = 0; i < NUMBER_OF_TRANSACTIONS; i++) {
				var startTime = performance.now()

				// console.log(contract.network.getChannel().getEndorser("peer0.org1.example.com:7051"))
				// contract.network.getChannel().removeEndorser(contract.network.getChannel().getEndorser("peer0.org1.example.com:7051"))
				assetName = 'asset' + i
				var result = await contract.submitTransaction('CreateAsset', assetName , "yellow", 1, "Gina", 1000)


				if (`${result}` !== '') {
					// console.log(`*** Result: ${prettyJSONString(result.toString())}`);
					console.log("")
					console.log(assetName +  ` added!!`);
				}

				var endTime = performance.now()

				var time = endTime - startTime


			}

			// 			//
			// 			// const mspId = gateway.getIdentity().mspId;
			// 			// var targets = contract.network.getChannel().getEndorsers(mspId);
			// 			//
			// 			// console.log(targets)
			//
			for (let i = 0; i < NUMBER_OF_TRANSACTIONS; i++) {
				var startTime = performance.now()

				assetName = 'asset' + i


				result = await contract.submitTransaction('DeleteAsset', assetName)
				if (`${result}` !== '') {
					// console.log(`*** Result: ${prettyJSONString(result.toString())}`);
					console.log("")
					console.log(assetName +  ` removed!`);
				}

			}

		} finally {
			// Disconnect from the gateway when the application is closing
			// This will close all connections to the network
			gateway.disconnect();
		}
	} catch (error) {
		console.error(`******** FAILED to run the application: ${error}`);
	}
}

main();



//let endorsera = contract.network.getChannel().client.getEndorsers()
//console.log(endorsera)
//  let endorsers = []
//  let orgNum = 0
// for (let i = 0; i < 8; i++) {
// 	orgNum = i + 1
// 	let portSuffix = (i * 2) + 7
// 	let endorser = contract.network.getChannel().getEndorser("peer0.org"+ orgNum + ".example.com:"+ portSuffix +"051")
//
// 	if(endorser!=undefined){
// 		endorsers.push(endorser)
// 	}
//
// }
//
// for (let i=4 ; i < 8 ; i ++){
// 	orgNum = i+1
// 	let portSuffix = (i * 2) + 7
//
// 	console.log("peer0.org"+ orgNum + ".example.com:"+ portSuffix +"051 ----> REMOVED!")
//
// 	//contract.network.getChannel().removeEndorser(endorsers[i])
// }
//
// for (var endorser of endorsers){
// 	console.log(endorser)
//  }



// console.log("Rimosso!")
//
// /// I can save it and reinsert it
// var tmp = contract.network.getChannel().getEndorser("peer0.org1.example.com:7051")
// console.log("Rimosso!")
// contract.network.getChannel().removeEndorser(tmp)
// contract.network.getChannel().addEndorser(tmp)
//
// console.log("Rimesso!")
// console.log(contract.network.getChannel().getEndorser("peer0.org1.example.com:7051"))
