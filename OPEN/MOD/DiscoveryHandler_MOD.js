/*
 Copyright 2019 IBM All Rights Reserved.

 SPDX-License-Identifier: Apache-2.0
*/

const TYPE = 'DiscoveryHandler';
const Long = require('long');
const settle = require('promise-settle');
const ServiceHandler = require('./ServiceHandler.js');
const fabproto6 = require('fabric-protos');
const {randomize, checkParameter, getLogger, getConfigSetting, convertToLong} = require('./Utils.js');
const logger = getLogger(TYPE);
const BLOCK_HEIGHT = 'ledgerHeight';
const RANDOM = 'random';

const fs = require('fs');
const { performance } = require('perf_hooks');

//#### OPTIMAL ENDORSEMENT POLICY

/**
 * TO select the mode:
 * ["ORIGINAL"] --> ORIGINAL
 * ["OPEN"]     --> OPEN
 * ["RND"]      --> RND_HALF
 * ["RND", N]   --> RND_N
 */
let MODE = ["OPEN"]

//#### OTHER VALUES
const NUM_ORG = 8;
const timestamp = performance.now();

//#### OPEN PARAMETERS
let T = 10;
const eps = 0.001; /// (1ms) IMAN: 0.001 = 1ns


class optimalEndorsementModule{
  // transaction number
  n = -1;
  // Data structures for OPEN algorithm
  peers = [];
  delays = [];
  eligibility = [];

  // parameters
  constructor(){
    this.initialized = false;
  }

  isInitialized(){
    return this.initialized;
  }

  /**
   * POSSIBLE OPTIONS:
   *   1. f("OPEN"), SENDS FOR 4 TXS ENDORSEMENT TO ALL THE PEERS AND THEN USES OPEN ALGORITHM
   *   2. f("RND", NUMBER_OF_RANDOM_PEER(S)) <=== IF NOT SET THE DEFAULT RANDOM PEER 2
   */
  bootUp(mode, totalRandom){
    console.log("[Bootup phase]: Initializing module");

    // TELLS US IF THE PEER IS ELEGIBLE TO ENDORSE THE NEXT TRANSACTION
    this.eligibility = new Array(NUM_ORG)

    for (var i = 0; i<this.eligibility.lenght; i++) {
      this.eligibility[i] = false
    }

    this.delays = new Array(2);
    this.peers = new Array(2);

    for (var i = 0; i<this.peers.length; i++) {
      this.delays[i] = new Array(NUM_ORG);
      this.peers[i] = new Array(NUM_ORG);
    }

    // PEER STRUCTURE INITIALIZATION
    for (var i = 0; i<this.peers.length; i++) {
      for (var j = 0; j<NUM_ORG; j++) {
        this.delays[i][j] = -1;
        this.peers[i][j] = false;
      }
    }

    this.n = 1
    this.initialized = true;
    this.mode = mode

    if (this.mode!= "RND"){
      console.log("                                    [ALGORITMH SELECTED]: " + mode + "." )
    }

    if(this.mode == "RND"){
      if(totalRandom != undefined){
        this.totalRandom = totalRandom
        this.INITIAL_DELAY_AQUIRING_STEP = 0
      } else {
        console.log("[BOOTUP] : Number of random peer to endorse not specified. Using value of half of the peers.")
        this.totalRandom = Math.floor(NUM_ORG/2)
      }
      console.log("                                    [ALGORITMH SELECTED]: " + mode + "_" + totalRandom + "." )
    } else if (this.mode == "OPEN") {
      this.INITIAL_DELAY_AQUIRING_STEP = Math.floor(NUM_ORG/2)
    }
  }


  /*###################################  GETTERS  ###################################*/
  //#### getLayout() RETURNS THE LAYOUT ACCORDING TO THE CHOSEN POLICY.
  getLayout(){
    console.log("-------------------------------------------------------->" + this.n);

      // ANY SUGGESTION FOR THE NAME?
      if ( this.n < this.INITIAL_DELAY_AQUIRING_STEP ){
        OEM.selectEndorsers("INITIAL_STEPS")
      } else {
        OEM.selectEndorsers();
      }

      console.log(OEM.getNamedEndorsement(0))

      this.n = this.n + 1;
      return this.peers[0].slice();
  }

  /**
   * getNamedEndorsement(t) transforms from [true, false, false, false, false, false, false, true]
   * to [peer0.org1.example.com, peer0.org8.example.com].
   * "t" parameter indicates which endorsement we want returned.
   * if      : t == 0 ==> ACTUAL
   * else if : t == 1 ==> PAST
   */
  getNamedEndorsement(t){
    if (t>1 || t<0){
      console.log("[getNamedEndorsement]: t must be between 0 and 1. Exit.");
      exit();
    }
    let endorsingVector = [];
    let i = 0;
    for (let i = 0; i<NUM_ORG; i++){
      if (this.peers[t][i] == true){
        let orgNum = i+1;
        let peerToAdd = "peer0.org" + orgNum + ".example.com";
        endorsingVector.push(peerToAdd);
      }
    }
    return endorsingVector;
  }

  /* ################################### SETTERS  ################################### */
  //#### setEndorsementDelays() sets the delays that were just measured.
  setEndorsementDelays(delay_data){
    OEM.prepareDelays()
    this.delays[0] = extractDelays(delay_data)
  }

  /* ################################### UTILS  ################################### */
  /**
   * selectEndorsers(MODE) chooses the next endorsement depending on the MODE
   * MODE is optional and if not specified uses the MODE chosen at construction time.
   *   -OPEN
   *   -SELECT_ALL
   *   -INITIAL_STEPS
   */
  selectEndorsers(ENDORSERS_SELECTION_ALGORITHM){
    if (this.n != 1){
      OEM.preparePeers()
    }

    // IF NO MODE GETS SPECIFIED IT DOES THE ONE IT WAS AT FIRST DEFINED ON THE CONSTRUCTOR
    if (ENDORSERS_SELECTION_ALGORITHM == undefined){
      ENDORSERS_SELECTION_ALGORITHM = this.mode
    }

    if (ENDORSERS_SELECTION_ALGORITHM == "OPEN"){
      // Max delay among endorsements to be used later
      let dMax = -1
      for (var i = 0; i<NUM_ORG; i++){
        if (this.peers[1][i] == true && this.delays[0][i] > dMax){
          dMax = this.delays[0][i];
        }
      }

      if (dMax == -1){ // no response from TX-1
        for (var i = 0; i<NUM_ORG; i++){ // all peers
          this.delays[0][i] = this.delays[1][i]; // use previous delays
          if (this.peers[1][i] == true){ // if was endorser
            this.elegibility[i] = false; // make it NOT-eligible
          }
        }
      } else { // We have response from TX-1
        for (var i = 0; i<NUM_ORG; i++){ // all peers
          if (this.peers[1][i] == true){ // if was endorser
            if (this.delays[0][i] == -1){ // if no response
              this.delays[0][i] = dMax + eps; // speculate it
              this.elegibility[i] = false; // make it NOT-eligible
            }
          } else { // if was NOT endorser
            this.delays[0][i] = this.delays[1][i]; // use previous delays
          }
        }
      }

      this.peers[0] = this.selectBestPeers(Math.floor(NUM_ORG/2), this.delays[0].slice()).slice();

      if (this.n%T == 0){
        OEM.endorseRandomPeer();
      }
      // console.log("The estimated/real delay values of the past transactions are:")
      // console.log(this.delays[0])

    } else if (ENDORSERS_SELECTION_ALGORITHM == "SELECT_ALL" || ENDORSERS_SELECTION_ALGORITHM == "INITIAL_STEPS"){
      this.peers[0] = this.peers[0].map(x =>x = true);
    } else if (ENDORSERS_SELECTION_ALGORITHM == "RND") {
      for (let i = 0 ; i < this.totalRandom ; i ++ ) {
        this.endorseRandomPeer()
      }
    }
  }

  //#### prepareDelays() shifts this.delays structure.
  prepareDelays(){
    // INITIALIZING DELAYS VECTOR
    this.delays[1] = this.delays[0].slice();
    this.delays[0] = this.delays[0].map(x => x = -1);

    // INITIALIZING PEERS VECTOR
    // this.readyForNextTransaction = true;
  }

  //#### preparePeers() shifts this.peers structure.
  preparePeers(){
    // Initialize eligibility vector for all peers
    this.eligibility = this.eligibility.map(x => x = true);

    // INITIALIZING PEERS VECTOR
    this.peers[1] = this.peers[0].slice();
    this.peers[0] = this.peers[0].map(x => x = false);

    // to not overwrite the delays and peers values
    // this.readyForNextTransaction = true;
  }

  //#### selectBestPeers(n,vector) selects n peers with lowest delays in vector
  selectBestPeers(n, vector){
    // EMPTY STRUCTURE WHICH WILL CONTAIN THE PEER THAT ARE SELECTED
    let selectedPeers = new Array(NUM_ORG).fill(false)

    let dMax = Math.max(...vector);
    for (var i = 0; i<n; i++){
      let dMin = dMax;
      let indMin = -1;
      // SELECTS THE PEER WITH MINIMUM LATENCY(REAL MEASURED OR ESTIMATED) (BEING CAREFUL TO NOT CONSIDER VALUES SMALLER THAN 0 (LIKE -1, WHICH MEANS THAT NO RESPONSE WAS RECEIVED.))
      for (var j = 0; j<NUM_ORG; j++){
        if (vector[j] != -1 && vector[j] <= dMin && selectedPeers[j]==false){
          dMin = vector[j];
          indMin = j;
        }
      }
      if (indMin!= -1){
        selectedPeers[indMin] = true;
      }
    }
    return selectedPeers;
  }

  //#### endorseRandomPeer() adds a random peer in the endorsement
  endorseRandomPeer(){
    let tmpRndPeers = []
    for (var i = 0; i<NUM_ORG; i++){
      if (this.peers[0][i] == false){
        tmpRndPeers.push(i);
      }
    }
    let done = false
    if (tmpRndPeers) {
      let randomIndex = this.getRandomInt(0,tmpRndPeers.length);
      this.peers[0][tmpRndPeers[randomIndex]] = true;
    }
  }

  //#### getRandomInt(i) generates a random int value in the [min,max) interval
  getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min) + min); //The maximum is exclusive and the minimum is inclusive
  }

  //#### fromIndexToName(i) transforms from 1 ==> peer0.org1.example.com
  fromIndexToName(i){
    let orgNum = i + 1;
    return "peer0.org" + orgNum + ".example.com";
  }
}


function extractDelays(delay_data) {
  let end_delays = new Array(NUM_ORG).fill(-1);

  for ( let i = 0 ; i < end_delays.lenght; i++ ){
    end_delays[i] = -1;
  }

  for (const key of Object.keys(delay_data[3][0])) {
    let peer_num = parseInt(key[1]);

    if (delay_data[3][1].hasOwnProperty(key)){
      end_delays[peer_num] = parseFloat(delay_data[3][1][key] - delay_data[3][0][key]);
    }
  }
  return end_delays.slice()
}

let OEM = new optimalEndorsementModule(); // IL:???

function getOEM(){
  if(MODE[0] == "ORIGINAL"){
    return undefined;
  } else if ( MODE[0] == "OPEN" || MODE[0] == "RND"){
    if (OEM.isInitialized() == false){
      OEM.bootUp( MODE[0], MODE[1] )
    }
    return OEM
  } else {
    console.log("[ERROR]: You inserted a wrong algorithm. Exiting.")
    exit(0)
  }
}


/**
 * This is an implementation for a handler.
 *
 * @class
 * @extends ServiceHandler
 */
class DiscoveryHandler extends ServiceHandler {

	/**
	 * constructor
	 *
	 * @param {DiscoveryService} discoveryService - The discovery service for this handler.
	 */
	constructor(discoveryService) {
		logger.debug('DiscoveryHandler.constructor - start');
		super();
		this.discoveryService = discoveryService;
		this.type = TYPE;
	}

	/**
	 * This will send transactions to all peers found by discovery.
	 * @param {*} signedProposal
	 * @param {Object} request - Include a 'mspid' when just peers from
	 *  an organization are required
	 */
	async query(signedProposal = checkParameter('signedProposal'), request = {}) {
		const method = 'query';
		logger.debug('%s - start', method);

		const {requestTimeout, mspid} = request;
		let results;

		let timeout = getConfigSetting('requestTimeout');
		if (requestTimeout) {
			timeout = requestTimeout;
		}

		// forces a refresh if needed
		//AO
		await this.discoveryService.getDiscoveryResults(true);
		const responses = [];
		const endorsers = this.discoveryService.channel.getEndorsers(mspid);
		if (endorsers && endorsers.length > 0) {
			logger.debug('%s - found %s endorsers assigned to channel', method, endorsers.length);
			const promises = endorsers.map(async (endorser) => {
				return endorser.sendProposal(signedProposal, timeout);
			});
			results = await settle(promises);
			results.forEach((result) => {
				if (result.isFulfilled()) {
					logger.debug(`query - Promise is fulfilled: ${result.value()}`);
					responses.push(result.value());
				} else {
					logger.debug(`query - Promise is rejected: ${result.reason()}`);
					responses.push(result.reason());
				}
			});
		} else {
			throw new Error('No endorsers assigned to the channel');
		}

		return responses;
	}

	/**
	 * This will submit transactions to be committed to one committer at a
	 * time from a list currently assigned to the channel.
	 * @param {*} signedProposal
	 * @param {Object} request
	 */
	async commit(signedEnvelope = checkParameter('signedEnvelope'), request = {}) {
		const method = 'commit';
		logger.debug('%s - start', method);

		const {requestTimeout, mspid} = request;

		let timeout = getConfigSetting('requestTimeout');
		if (requestTimeout) {
			timeout = requestTimeout;
		}

		// force a refresh if needed
		await this.discoveryService.getDiscoveryResults(true);

		const committers = this.discoveryService.channel.getCommitters(mspid);
		if (committers && committers.length > 0) {
			logger.debug('%s - found %s committers assigned to channel', method, committers.length);
			randomize(committers);

			let results;
			// first pass only try a committer that is in good standing
			results = await this._commitSend(committers, signedEnvelope, timeout, false);
			if (results.error) {
				// since we did not get a good result, try another pass, this time try to
				// have the orderers reconnect
				results = await this._commitSend(committers, signedEnvelope, timeout, true);
			}

			if (results.commit) {
				logger.debug('%s - return commit status %s ', method, results.commit);
				return results.commit;
			}

			logger.debug('%s - return error %s ', method, results.error);
			throw results.error;
		} else {
			throw new Error('No committers assigned to the channel');
		}
	}

	async _commitSend(committers, signedEnvelope, timeout, reconnect) {
		const method = 'commit';
		logger.debug('%s - start', method);

		let return_error;
		// loop through the committers trying to complete one successfully
		for (const committer of committers) {
			logger.debug('%s - sending to committer %s', method, committer.name);
			try {
				const isConnected = await committer.checkConnection(reconnect);
				if (isConnected) {
					const commit = await committer.sendBroadcast(signedEnvelope, timeout);
					if (commit) {
						if (commit.status === 'SUCCESS') {
							logger.debug('%s - Successfully sent transaction to the committer %s', method, committer.name);
							return {error: undefined,  commit};
						} else {
							logger.debug('%s - Failed, status was not "success" from the send transaction to the committer. status:%s', method, commit.status);
							return_error = new Error('Failed to send transaction successfully to the committer. status:' + commit.status);
						}
					} else {
						return_error = new Error('Failed to receive committer status');
						logger.debug('%s - Failed, no status received on the send transaction to the committer %s', method, committer.name);
					}
				} else {
					let error_message = `Failed, committer ${committer.name} is not connected`;
					if (reconnect) {
						error_message = `Failed, not able to reconnect to committer ${committer.name}`;
					}
					return_error = new Error(error_message);
				}
			} catch (error) {
				logger.debug('%s - Caught: %s', method, error.toString());
				return_error = error;
			}
		}

		logger.debug('%s - return error %s ', method, return_error.toString());
		return {error: return_error};
	}

	/**
	 * This method will submit transactions to be endorsed to endorsers as
	 * determined by the endorser's discovery service
	 * @param {*} signedProposal
	 * @param {*} request
	 */
	async endorse(signedProposal = checkParameter('signedProposal'), request = {}) {/// IMAN: is OPEN recognized here?!
		const method = 'endorse';
		logger.debug('%s - start', method);

		let timeout = getConfigSetting('requestTimeout');
		if (request.requestTimeout) {
			timeout = request.requestTimeout;
		}

    let endorse_time = []

    // IL: pure start time => (0)
    endorse_time.push(performance.now());

    const results = await this.discoveryService.getDiscoveryResults(true); //// IMAN: we need the sample response to generate for OPEN.

    // console.log(" G0 -------------> " + results.endorsement_plan.groups.G0.peers[0].mspid)
    // console.log(" G1 -------------> " + results.endorsement_plan.groups.G1.peers[0].mspid)

    // IL: After discovery service responce start time => (1)

    endorse_time.push(performance.now());

    if (MODE[0] == "ORIGINAL"){
      // const results = await this.discoveryService.getDiscoveryResults(true); //// IMAN: we need the sample response to generate for OPEN.
      if (results && results.peers_by_org && request.requiredOrgs) {
        // special case when user knows which organizations to send the endorsement
        // let's build our own endorsement plan so that we can use the sorting and sending code
        const endorsement_plan = this._buildRequiredOrgPlan(results.peers_by_org, request.requiredOrgs);
        // console.log("ok")
        // remove conflicting settings
        const orgs_request = {
          sort: request.sort,
          preferredHeightGap: request.preferredHeightGap
        };

        return this._endorse(endorsement_plan, orgs_request, signedProposal, timeout, endorse_time);
      } else if (results && results.endorsement_plan) {
        // normal processing of the discovery results
        const working_discovery = JSON.parse(JSON.stringify(results.endorsement_plan));

        return this._endorse(working_discovery, request, signedProposal, timeout, endorse_time);
      } else if (results && results.peers_by_org) {
        // special case when the chaincode is system chaincode without an endorsement policy
        const endorsement_plan = this._buildAllOrgPlan(results.peers_by_org);

        return this._endorse(endorsement_plan, request, signedProposal, timeout);
      } else {
        throw Error('No endorsement plan available');
      }

    } else {
      // "OPEN"  ///// need to read from OEM.peers[0] or endorsers
      ///TODO IMAN: should follow => JSON.parse(JSON.stringify(whatever is after = in the next lines)
      // const endorsement_plan = {chaincode: 'basic',
      // groups: {G0:[Object],G1:[Object],G2:[Object],G3:[Object],G4:[Object],G5:[Object],G6:[Object],G7:[Object]},
      // layouts: [[open_layout]]
      // };
      // what is "Long" after ledgerHeight????
      const endorsement_plan = {
         "chaincode": 'basic',
         "groups" : {
           "G0" : {
             "peers": [{
               "mspid": 'Org1MSP',
               "endpoint": 'peer0.org1.example.com:7051',
               "name": 'peer0.org1.example.com:7051',
               "ledgerHeight": { "low": 18, "high": 0, "unsigned": true },
               "chaincodes": [{ "name": 'basic', "version": '1'}, { "name": '_lifecycle', "version": '1'}]
             }]
           },
           "G1" : {
             "peers": [{
               "mspid": 'Org2MSP',
               "endpoint": 'peer0.org2.example.com:9051',
               "name": 'peer0.org2.example.com:9051',
               "ledgerHeight": { "low": 18, "high": 0, "unsigned": true },
               "chaincodes": [{ "name": 'basic', "version": '1'}, { "name": '_lifecycle', "version": '1'}]
             }]
           },
           "G2" : {
             "peers": [{
               "mspid": 'Org3MSP',
               "endpoint": 'peer0.org3.example.com:11051',
               "name": 'peer0.org3.example.com:11051',
               "ledgerHeight": { "low": 18, "high": 0, "unsigned": true },
               "chaincodes": [{ "name": 'basic', "version": '1'}, { "name": '_lifecycle', "version": '1'}]
             }]
           },
           "G3" : {
             "peers": [{
               "mspid": 'Org4MSP',
               "endpoint": 'peer0.org4.example.com:13051',
               "name": 'peer0.org4.example.com:13051',
               "ledgerHeight": { "low": 18, "high": 0, "unsigned": true },
               "chaincodes": [{ "name": 'basic', "version": '1'}, { "name": '_lifecycle', "version": '1'}]
             }]
           },
           "G4" : {
             "peers": [{
               "mspid": 'Org5MSP',
               "endpoint": 'peer0.org5.example.com:15051',
               "name": 'peer0.org5.example.com:15051',
               "ledgerHeight": { "low": 18, "high": 0, "unsigned": true },
               "chaincodes": [{ "name": 'basic', "version": '1'}, { "name": '_lifecycle', "version": '1'}]
             }]
           },
           "G5" : {
             "peers": [{
               "mspid": 'Org6MSP',
               "endpoint": 'peer0.org6.example.com:17051',
               "name": 'peer0.org6.example.com:17051',
               "ledgerHeight": { "low": 18, "high": 0, "unsigned": true },
               "chaincodes": [{ "name": 'basic', "version": '1'}, { "name": '_lifecycle', "version": '1'}]
             }]
           },
           "G6" : {
             "peers": [{
               "mspid": 'Org7MSP',
               "endpoint": 'peer0.org7.example.com:19051',
               "name": 'peer0.org7.example.com:19051',
               "ledgerHeight": { "low": 18, "high": 0, "unsigned": true },
               "chaincodes": [{ "name": 'basic', "version": '1'}, { "name": '_lifecycle', "version": '1'}]
             }]
           },
           "G7" : {
             "peers": [{
               "mspid": 'Org8MSP',
               "endpoint": 'peer0.org8.example.com:21051',
               "name": 'peer0.org8.example.com:21051',
               "ledgerHeight": { "low": 18, "high": 0, "unsigned": true },
               "chaincodes": [{ "name": 'basic', "version": '1'}, { "name": '_lifecycle', "version": '1'}]
             }]
           }
         },
         "layouts": [{}]
       };

      let optimizedLayout = getOEM().getLayout();

      let base_layout = { "G0": 1, "G1": 1, "G2": 1, "G3": 1, "G4": 1, "G5": 1, "G6": 1, "G7": 1};
      let i = 0;
      for (const group_name in base_layout) {
        if (optimizedLayout[i] == true){
          var group = base_layout[i];
          endorsement_plan["layouts"][0][group_name] = 1;
        }
        i = i+1;
      }

      results.endorsement_plan = endorsement_plan; // IL: let's check if possible

      return this._endorse(endorsement_plan, request, signedProposal, timeout, endorse_time, getOEM());
    }
  }

	async _endorse(endorsement_plan = checkParameter('endorsement_plan'), request = {}, proposal = checkParameter('proposal'), timeout, endorse_time, opt='None') {
		const method = '_endorse';

		logger.debug('%s - starting', method);
		endorsement_plan.endorsements = {};
		const results = {};
		results.endorsements = null; // will be from just one layout
		results.failed_endorsements = []; // from all failed layouts
		results.success = false;

		const required = this._create_map(request.required, 'endpoint');
		const preferred = this._create_map(request.preferred, 'endpoint');
		const ignored = this._create_map(request.ignored, 'endpoint');
		const required_orgs = this._create_map(request.requiredOrgs, 'mspid');
		const preferred_orgs = this._create_map(request.preferredOrgs, 'mspid');
		const ignored_orgs = this._create_map(request.ignoredOrgs, 'mspid');

		let preferred_height_gap = Long.fromInt(1); // default of one block
		try {
			if (Number.isInteger(request.preferredHeightGap) || request.preferredHeightGap) {
				preferred_height_gap = convertToLong(request.preferredHeightGap, true);
			}
		} catch (error) {
			throw Error('preferred_height_gap setting is not a number');
		}

		let sort = BLOCK_HEIGHT;
		if (request.sort) {
			if (request.sort === BLOCK_HEIGHT) {
				sort = BLOCK_HEIGHT;
			} else if (request.sort === RANDOM) {
				sort = RANDOM;
			} else {
				throw Error('sort parameter is not valid');
			}
		}

		// fix the peer group lists to reflect the options the user has provided
		this._modify_groups(
			required,
			preferred,
			ignored,
			required_orgs,
			preferred_orgs,
			ignored_orgs,
			preferred_height_gap,
			sort,
			endorsement_plan
		);

		// always randomize the layouts
		endorsement_plan.layouts = this._getRandom(endorsement_plan.layouts);

		let matchError = false;

		// loop through the layouts trying to complete one successfully
		for (const layout_index in endorsement_plan.layouts) {
			logger.debug('%s - starting layout plan %s', method, layout_index);
			const layout_results = await this._endorse_layout(layout_index, endorsement_plan, proposal, timeout, endorse_time, opt);
			// if this layout is successful then we are done
			if (layout_results.success) {
        // make sure all responses have the same endorsement read/write set
				//double check -->errors
				if (this.compareProposalResponseResults(layout_results.endorsements)) {
					logger.debug('%s - layout plan %s completed successfully', method, layout_index);
					results.endorsements = layout_results.endorsements;
					results.success = true;
					break;
				} else {
					matchError = true;
				}
			}
			logger.debug('%s - layout plan %s did not complete successfully', method, layout_index);
			results.failed_endorsements = results.failed_endorsements.concat(layout_results.endorsements);
		}

		if (!results.success) {
			let error;
			if (matchError) {
				error = new Error('Peer endorsements do not match');
			} else {
				error = new Error('Endorsement has failed');
			}
			error.endorsements = results.failed_endorsements;
			return [error];
		}
		return results.endorsements;
	}

  async _endorse_layout(layout_index, endorsement_plan, proposal, timeout, endorse_time, opt) {
		const method = '_endorse_layout';
    logger.debug('%s - start', method);

    const results = {};
		results.endorsements = [];
		results.success = true;
    let layout = endorsement_plan.layouts[layout_index];
    let endorser_process_index = 0;
		const endorsers = [];

    //#### OPTIMAL ENDORSEMENT POLICY
    let timeMeasured = 0;
    let avg = 0;
    let sumTime = 0;
    let count = 0;

    endorse_time.push(performance.now());
    // IL: [{group_name:start_time},{group_name:finishe_time}] for peers in Layout => (3)
    endorse_time.push([{},{}]);
    for (const group_name in layout) { // IL: everything is officially starting here
      // IL: update the related group_name(i.e. peer) start time
      endorse_time[3][0][group_name] = performance.now();
      const required = layout[group_name];
      const group = endorsement_plan.groups[group_name];
      // make sure there are enough peers in the group to satisfy required
      if (required > group.peers.length) {
        results.success = false;
        const error = new Error(`Endorsement plan group does not contain enough peers (${group.peers.length}) to satisfy policy (required:${required})`);
        logger.debug(error.message);
        results.endorsements.push(error);
        break; // no need to look at other groups, this layout failed
      }
      for (let x = 0; x<required; x++) {
        const endorser_process =
          this._build_endorse_group_member(endorsement_plan, group, proposal, timeout, endorser_process_index++, group_name, endorse_time);
        endorsers.push(endorser_process);
      }
    } // IL: an "endorser_process" has been built and is put as an endorser in endorsers

    // this part is waiting for the response of the whole layout.(we need to separate them)
		if (results.success) {
			results.endorsements = await this._execute_endorsements(endorsers, endorse_time,opt);

      for (const endorsement of results.endorsements) {
        if (endorsement instanceof Error) {
          results.success = false;
        } else if (typeof endorsement.success === 'boolean' && endorsement.success === false) {
          results.success = false;
        }
      }
      // IL: Layout finish time (repeated for being sure) => (5)
      endorse_time.push(performance.now());
    }

    if (MODE[0] != "ORIGINAL"){
      opt.setEndorsementDelays(endorse_time);
    }

    // IL: NOT SURE ABOUT THIS PART
    ///// VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV /////
    let tmpDelays1 = extractDelays(endorse_time).filter((value) => { if(parseFloat(value)!= -1) { return value; }});

    let DELAYFile

    //#### FILE NAMES
    if (MODE[0] == "OPEN"){
      DELAYFile = "./results/OPENEndTimesT"+T+"eps"+eps+"_"+timestamp+".txt";
    } else if (MODE[0] == "RND"){
      DELAYFile = "./results/RNDHalfEndTimes_"+timestamp+".txt";
    } else if (MODE[0] == "ORIGINAL"){
      DELAYFile = "./results/NormalEndTimes_"+timestamp+".txt";
    }


    if (tmpDelays1.length != 0){ // this condition is wrong
      let minDelay = parseFloat(tmpDelays1[0]);

      for (let value of tmpDelays1 ){
        let tmp = parseFloat(value)
        if (tmp > 0 && tmp < minDelay){
          minDelay = tmp;
        }
      }

      timeMeasured = endorse_time[5] - endorse_time[0];
      sumTime = sumTime + timeMeasured;
      count = count + 1;
      avg = sumTime/count;

      console.log("Ave. T: " + avg +" # Layout end. T: "+timeMeasured+" # Min end. delay: "+minDelay);
      fs.appendFile(DELAYFile, JSON.stringify(endorse_time) + '\n' , function(err) {if(err) {return console.log(err);}});
    } else {
      fs.appendFile(DELAYFile, "No responses were recorded!" + '\n');
      console.log("No responses were recorded!")
    }

    return results;
  }

	async _execute_endorsements(endorser_processes, endorse_time) {
		const method = '_execute_endorsements';
		logger.debug('%s - start', method);

		const results = await Promise.all(endorser_processes);
		const responses = [];
		for (const result of results) {
			if (result instanceof Error) {
				logger.debug('%s - endorsement failed: %s', method, result);
			} else {
				logger.debug('%s - endorsement is complete', method);
			}
			responses.push(result);
		}
    // IL: Layout finish time => (4)
    endorse_time.push(performance.now());

		return responses;
	}

	_buildRequiredOrgPlan(peers_by_org, required_orgs) {
		const method = '_buildRequiredOrgPlan';
		logger.debug('%s - starting', method);
		const endorsement_plan = {plan_id: 'required organizations'};
		endorsement_plan.groups = {};
		endorsement_plan.layouts = [{}]; // only one layout which will have all organizations
		const notFound = [];

		for (const mspid of required_orgs) {
			logger.debug(`${method} - found org:${mspid} `);
			endorsement_plan.groups[mspid] = {}; // make a group for each
			if (peers_by_org[mspid] && peers_by_org[mspid].peers && peers_by_org[mspid].peers.length > 0) {
				endorsement_plan.groups[mspid].peers = JSON.parse(JSON.stringify(peers_by_org[mspid].peers)); // now put in all peers from that organization
				endorsement_plan.layouts[0][mspid] = 1; // add this org to the one layout and require one peer to endorse
			} else {
				logger.debug('%s - discovery plan does not have peers for %', method, mspid);
				notFound.push(mspid);
			}
		}

		if (notFound.length > 0) {
			throw Error(`The discovery service did not find any peers active for ${notFound} organizations`);
		}
		return endorsement_plan;
	}

	_buildAllOrgPlan(peers_by_org) {
		const method = '_buildAllOrgPlan';
		logger.debug('%s - starting', method);
		const endorsement_plan = {plan_id: 'all organizations'};
		endorsement_plan.groups = {};
		endorsement_plan.layouts = [{}]; // only one layout which will have all organizations
		let notFound = true;

		Object.keys(peers_by_org).forEach((mspid) => {
			const org = peers_by_org[mspid];
			if (org.peers && org.peers.length > 0) {
				endorsement_plan.groups[mspid] = {}; // make a group for each
				endorsement_plan.groups[mspid].peers = JSON.parse(JSON.stringify(org.peers)); // now put in all peers from that organization
				endorsement_plan.layouts[0][mspid] = 1; // add this org to the one layout and require one peer to endorse
				notFound = false;
			} else {
				logger.debug('%s - discovery plan does not have peers for %', method, mspid);
			}
		});

		if (notFound) {
			throw Error('The discovery service did not find any peers active');
		}
		return endorsement_plan;
	}

	/*
	 * utility method to build a promise that will return one of the required
	 * endorsements or an error object
	 */

   _build_endorse_group_member(endorsement_plan, group, proposal, timeout, endorser_process_index, group_name) {
   const method = '_build_endorse_group_member >> ' + group_name + ':' + endorser_process_index;
   logger.debug('%s - start', method);

   // eslint-disable-next-line no-async-promise-executor
   return new Promise(async (resolve) => {
     let endorsement = null;
     for (const peer_info of group.peers) {
       endorsement = endorsement_plan.endorsements[peer_info.name];
       if (endorsement) {
         logger.debug('%s - existing peer %s endorsement will be used', method, peer_info.name);
       } else {
         if (peer_info.in_use) {
           logger.debug('%s - peer in use %s, skipping', method, peer_info.name);
         } else {
           const peer = this._getPeer(peer_info.endpoint);
           if (peer) {
             logger.debug('%s - send endorsement to %s', method, peer_info.name);
             peer_info.in_use = true;
             try {
               const isConnected = await peer.checkConnection();
               if (isConnected) {
                 endorsement = await peer.sendProposal(proposal, timeout);
                 // save this endorsement results in case we try this peer again
                 logger.debug('%s - endorsement completed to %s', method, peer_info.name);
               } else {
                 endorsement = peer.getCharacteristics(new Error(`Peer ${peer.name} is not connected`));
               }
             } catch (error) {
               endorsement = peer.getCharacteristics(error);
               logger.error('%s - error on endorsement to %s error %s', method, peer_info.name, error);
             }
             // save this endorsement results in case we try this peer again
             // eslint-disable-next-line require-atomic-updates
             endorsement_plan.endorsements[peer_info.name] = endorsement;
           } else {
             logger.debug('%s - peer %s not assigned to this channel', method, peer_info.name);
           }
         }
       }
       if (endorsement && !(endorsement instanceof Error)) {
         logger.debug('%s - peer %s endorsement will be used', method, peer_info.name);
         break;
       }
     }

     if (endorsement) {
       logger.debug('%s - returning endorsement', method);
       resolve(endorsement);
     } else {
       logger.error('%s - returning an error endorsement, no endorsement made', method);
       resolve(new Error('No endorsement available'));
     }
   });
 }

	_build_endorse_group_member(endorsement_plan, group, proposal, timeout, endorser_process_index, group_name, endorse_time) {
    const method = '_build_endorse_group_member >> ' + group_name + ':' + endorser_process_index;
    logger.debug('%s - start', method);


    // eslint-disable-next-line no-async-promise-executor
    return new Promise(async (resolve) => {
      let endorsement = null;

      for (const peer_info of group.peers) {
        endorsement = endorsement_plan.endorsements[peer_info.name];
        /////SEMBRA CHE LA RICHIESTA DI ENDORSEMENT LA MANDI SOLO A COLORO CHE NON SONO ENDORSERS
        if (endorsement) {
          logger.debug('%s - existing peer %s endorsement will be used', method, peer_info.name);
          // // } else {
          // 	if (peer_info.in_use) {
          // 		logger.debug('%s - peer in use %s, skipping', method, peer_info.name);
        } else {
          const peer = this._getPeer(peer_info.endpoint);
          if (peer) {
            logger.debug('%s - send endorsement to %s', method, peer_info.name);
            peer_info.in_use = true;
            try {
              ///////single endorsement sent
              /////// ENDORSEMENTS
              const isConnected = await peer.checkConnection();
              if (isConnected) {
                endorsement = await peer.sendProposal(proposal, timeout);
                // IL: update the related group_name(i.e. peer) finish time
                endorse_time[3][1][group_name] = performance.now();
                // endorsementTime[parseInt(peer_info.name.split(".")[1].replace("org",""))-1] = delay
                // save this endorsement results in case we try this peer again
                logger.debug('%s - endorsement completed to %s', method, peer_info.name);
              } else {
                endorsement = peer.getCharacteristics(new Error(`Peer ${peer.name} is not connected`));
              }
            } catch (error) {
              endorsement = peer.getCharacteristics(error);
              logger.error('%s - error on endorsement to %s error %s', method, peer_info.name, error);
            }
            endorsement_plan.endorsements[peer_info.name] = endorsement;
          } else {
            logger.debug('%s - peer %s not assigned to this channel', method, peer_info.name);
          }
          if (endorsement && !(endorsement instanceof Error)) {
            logger.debug('%s - peer %s endorsement will be used', method, peer_info.name);
            break;
          }
        }
      }

      if (endorsement) {
          logger.debug('%s - returning endorsement', method);
          resolve(endorsement);
        } else {
          logger.error('%s - returning an error endorsement, no endorsement made', method);
          resolve(new Error('No endorsement available'));
        }
    });
      // endorse_time[3][1][group_name] = performance.now();
    }


	/*
	 * utility method that will take a group of peers and modify the order
	 * of the peers within the group based on the user's requirements
	 *
	 * for each group
	 *  - remove the ignored and all non required
	 *  - sort group list by ledger height (larger on top) or randomly
	 *  - walk sorted list
	 *      -- put the preferred peers & organizations in the priority bucket if ledger height acceptable
	 *      -- put others in non priority bucket
	 *  - build final modified group (this will maintain how they were sorted)
	 *      -- pull peers from priority bucket
	 *      -- pull peers from non priority bucket
	 *  - return modified group
	 */
	_modify_groups(required, preferred, ignored, required_orgs, preferred_orgs, ignored_orgs, preferred_height_gap, sort, endorsement_plan) {
		const method = '_modify_groups';
		logger.debug('%s - start', method);
		logger.debug('%s - required:%j', method, required);
		logger.debug('%s - preferred:%j', method, preferred);
		logger.debug('%s - ignored:%j', method, ignored);
		logger.debug('%s - required_orgs:%j', method, required_orgs);
		logger.debug('%s - preferred_orgs:%j', method, preferred_orgs);
		logger.debug('%s - ignored_orgs:%j', method, ignored_orgs);
		logger.debug('%s - preferred_height_gap:%s', method, preferred_height_gap);
		logger.debug('%s - sort: %s', method, sort);
		logger.debug('%s - endorsement_plan:%j', method, endorsement_plan);

		for (const group_name in endorsement_plan.groups) {
			const group = endorsement_plan.groups[group_name];
			for (const peer of group.peers) {
				peer.ledgerHeight = new Long(peer.ledgerHeight.low, peer.ledgerHeight.high);
			}

			// remove ignored and non-required
			const clean_list = this._removePeers(ignored, ignored_orgs, required, required_orgs, group.peers);

			// get the highest ledger height if needed
			let highest = null;
			if (sort === BLOCK_HEIGHT) {
				highest = this._findHighest(clean_list);
			}

			// sort based on ledger height or randomly
			const sorted_list = this._sortPeerList(sort, clean_list);
			// pop the priority peers off the sorted list
			const split_lists = this._splitList(preferred, preferred_orgs, preferred_height_gap, highest, sorted_list);
			// put the priorities on top
			const reordered_list = split_lists.priority.concat(split_lists.non_priority);
			// set the rebuilt peer list into the group
			group.peers = reordered_list;
		}

		logger.debug('%s - updated endorsement_plan:%j', method, endorsement_plan);
	}

	_create_map(array) {
		const map = new Map();
		if (array && Array.isArray(array)) {
			array.forEach((item) => {
				map.set(item, item);
			});
		}

		return map;
	}

	/*
	 * utility method to remove peers that are ignored or not on the required list
	 */
	_removePeers(ignored_peers, ignored_orgs, required_peers, required_orgs, peers) {
		const method = '_removePeers';
		logger.debug('%s - start', method);

		const keep_list = [];
		for (const peer of peers) {
			let found = ignored_peers.has(peer.name);
			if (!found) {
				found = ignored_orgs.has(peer.mspid);
				if (!found) {
					// if the user has requested required peers/orgs
					// then all peers that stay on the list must be
					// one of those peers or in one of those orgs
					if (required_peers.size || required_orgs.size) {
						found = required_peers.has(peer.name);
						if (!found) {
							found = required_orgs.has(peer.mspid);
						}
						// if we did not find it on a either list then
						// this peer will not be added to the keep list
						if (!found) {
							continue; // do not add this peer to the keep list
						}
					}

					// looks like this peer is not on the ignored list and
					// is on the required list (if being used);
					keep_list.push(peer);
				}
			}
		}

		return keep_list;
	}

	_findHighest(peers) {
		let highest = Long.fromValue(0);
		for (const peer of peers) {
			try {
				if (peer.ledgerHeight.greaterThan(highest)) {
					highest = peer.ledgerHeight;
				}
			} catch (error) {
				logger.error('problem finding highest block with %s', error);
				throw Error(`Unable to find highest block value :: ${error.toString()}`);
			}
		}

		return highest;
	}

	_sortPeerList(sort, peers) {
		const method = '_sortList';
		logger.debug('%s - start - %s', method, sort);

		let sorted = null;

		if (sort === BLOCK_HEIGHT) {
			sorted = peers.sort((a, b) => {
				logger.debug('%s - sorting descending', method);
				if (a.ledgerHeight && !b.ledgerHeight) {
					logger.debug('%s - a exist (%s) - b does not exist', method, a.ledgerHeight);

					return -1;
				} else if (!a.ledgerHeight && b.ledgerHeight) {
					logger.debug('%s - a does not exist - b exist (%s)', method, b.ledgerHeight);

					return 1;
				} else {
					const result = -1 * a.ledgerHeight.compare(b.ledgerHeight);
					logger.debug('%s - compare result: %s for a:(%s) b:(%s) ', method, result, a.ledgerHeight.toString(), b.ledgerHeight.toString());

					return result;
				}
			});
		} else { // must be random
			sorted = this._getRandom(peers);
		}

		return sorted;
	}


	_splitList(preferred_peers, preferred_orgs, preferred_height_gap, highest, sorted_list) {
		const method = '_splitList';
		logger.debug('%s - start', method);

		const priority = [];
		const non_priority = [];

		for (const peer of sorted_list) {
			// first see if on the preferred lists
			let found = preferred_peers.has(peer.name);
			if (!found) {
				logger.debug('%s - peer %s not found on the preferred peer list', method, peer.name);
				found = preferred_orgs.has(peer.mspid);
				if (found) {
					logger.debug('%s - peer %s found on preferred org list', method, peer.name);
				} else {
					logger.debug('%s - peer %s not found on preferred org list', method, peer.name);
				}
			} else {
				logger.debug('%s - peer %s found on the preferred peer list', method, peer.name);
			}

			// if not on the preferred lists and we are sorting by block hieght
			// check the gap that indicates that it will be up to date shortly and it should be used
			if (!found && highest) {
				if (peer.ledgerHeight) {
					logger.debug('%s - checking preferred gap of %s', method, preferred_height_gap);
					logger.debug('%s - peer.ledgerHeight %s', method, peer.ledgerHeight);
					if (highest.subtract(peer.ledgerHeight).greaterThan(preferred_height_gap)) {
						found = false; // this peer should not be on the priority list
						logger.debug('%s -gap too big, peer should not be on priority list', method, peer.name);
					} else {
						found = true; // this peer should not be on the priority list
						logger.debug('%s - gap is OK, peer should be on priority list', method, peer.name);
					}
				} else {
					logger.debug('%s - peer has no ledgerHeight, not a priority peer');
					found = false;
				}

			} else {
				logger.debug('%s - not checking the preferred height gap', method);
			}
			if (found) {
				priority.push(peer);
			} else {
				non_priority.push(peer);
			}
		}

		// priority peers are all the same, try not to use the same
		// one everytime
		const randomized_priority = this._getRandom(priority);

		return {priority: randomized_priority, non_priority};
	}

	/*
	 * utility function to return a random list
	 */
	_getRandom(start_list) {
		let len = start_list.length;
		const result_list = new Array(len);
		const taken = new Array(len);
		let n = len;
		while (n--) {
			const x = Math.floor(Math.random() * len);
			result_list[n] = start_list[x in taken ? taken[x] : x];
			taken[x] = --len in taken ? taken[len] : len;
		}

		return result_list;
	}

	/*
	 * utility function to return a peer with the requested url
	 */
	_getPeer(address) {
		let result = null;
		if (address) {
			const host_port = address.split(':');
			const url = this.discoveryService._buildUrl(host_port[0], host_port[1]);
			const peers = this.discoveryService.channel.getEndorsers();
			for (const peer of peers) {
				if (peer.endpoint && peer.endpoint.url === url) {
					result = peer;
					break;
				}
			}
		}

		return result;
	}

	// internal utility method to decode and get the write set from an endorsement
	_getProposalResponseResults(proposaResponse = checkParameter('proposalResponse')) {
		if (!proposaResponse.payload) {
			throw new Error('Parameter must be a ProposalResponse Object');
		}
		const payload = fabproto6.protos.ProposalResponsePayload.decode(proposaResponse.payload);

		const extension = fabproto6.protos.ChaincodeAction.decode(payload.extension);

		return extension.results;
	}

	/**
	 * Utility method to examine a set of proposals to check they contain
	 * the same endorsement result write sets.
	 * This will validate that the endorsing peers all agree on the result
	 * of the chaincode execution.
	 *
	 * @param {ProposalResponse[]} proposalResponses - The proposal responses
	 * from all endorsing peers
	 * @returns {boolean} True when all proposals compare equally, false otherwise.
	 */
	compareProposalResponseResults(proposalResponses = checkParameter('proposalResponses')) {
		const method = `compareProposalResponseResults[${this.chaincodeId}]`;
		logger.debug('%s - start', method);

		if (!Array.isArray(proposalResponses)) {
			throw new Error('proposalResponses must be an array, typeof = ' + typeof proposalResponses);
		}
		if (proposalResponses.length === 0) {
			throw new Error('proposalResponses is empty');
		}

		if (proposalResponses.some((response) => response instanceof Error)) {

			return false;
		}

		const first_one = this._getProposalResponseResults(proposalResponses[0]);


		for (let i = 1; i<proposalResponses.length; i++) {
			const next_one = this._getProposalResponseResults(proposalResponses[i]);

			if (next_one.equals(first_one)) {
				logger.debug('%s - read/writes result sets match index = %s', method, i);
			} else {
				logger.error('%s - read/writes result sets do not match index = %s', method, i);
				return false;
			}
		}

		return true;
	}

	toString() {
		return `{type:${this.type}, discoveryService:${this.discoveryService.name}}`;
	}
}

module.exports = DiscoveryHandler;
