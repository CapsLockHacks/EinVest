import logging
import os
import sys
from logging import DEBUG
from os import curdir, getenv, path
from sys import exit

import requests as re

from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, session)
from kiteconnect import KiteConnect
from kiteconnect.exceptions import NetworkException
from config import KITE_API_KEY, KITE_REQUEST_TOKEN, KITE_SECRET
from scaffold import *

app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

app.secret_key = 'secret'

log.setLevel(DEBUG)

# xe.com
xe_account_id = 'student926567212'
xe_api_key = 'a77skb1r13cnrhjg5j8953nuvj'


def initialize_kite():
	"""
	Helper function to initialize Kite.
	"""
	kite = KiteConnect(api_key=KITE_API_KEY)

	try:
		with open('token.ini', 'r') as the_file:
			access_token = the_file.readline()
			try:
				kite.set_access_token(access_token)

			except Exception as e:
				log.error("Authentication failed {}".format(str(e)))
				raise

	except FileNotFoundError:
		try:
			user = kite.request_access_token(
				request_token=KITE_REQUEST_TOKEN, secret=KITE_SECRET)
		except Exception as e:
			log.error("{}".format(str(e)))
			exit()

		with open ('token.ini', 'w') as the_file:
			the_file.write(user['access_token'])

		try:
			kite.set_access_token(user["access_token"])

		except Exception as e:
			log.error("Authentication failed {}".format(str(e)))
			raise

	return kite


@app.route('/')
def index():
	return "Hello World"

@app.route('/place_order', methods=['GET'])
def place_order():
	kite_instance = initialize_kite()
	log.info(request.args)
	log.info(kite_instance)
	# Place an order
	try:
		order_id = kite_instance.order_place(tradingsymbol=request.args['tradingsymbol'],
						exchange="NSE",
						transaction_type=request.args['transaction_type'],
						quantity=1,
						order_type="MARKET",
						product="CNC")

		log.info("Order placed. ID is {}".format(order_id))
	except NetworkException:
		log.debug("SUCCESS")
		return jsonify({"result":200})

	return order_id

@app.route('/convert_rr/<val>/<_from>/<_to>', methods=['GET'])
def convert_real_to_real(val, _from, _to):
	if request.method == 'GET':
		params = (
			('from', _from),
			('to', _to),
			('amount', val),
		)

		resp = re.get('https://xecdapi.xe.com/v1/convert_from.json/', params=params, auth=(xe_account_id, xe_api_key))
		result = {"result": resp.json()["to"][0]["mid"], 'status': 'OK'}

		return jsonify(result)


@app.route('/create_market/<stock>/')
def create_market(stock):
	if request.method == 'GET':
		file_contents = """
const Gnosis = require('@gnosis.pm/gnosisjs');
const Web3 = require('web3');

const resolutionDate = new Date();
resolutionDate.setDate(resolutionDate.getDate() + 1);

const options = {
  ethereum: new Web3(new Web3.providers.HttpProvider('http://localhost:8545')).currentProvider,
  ipfs: {
    host: 'localhost',
    port: 5001,
    protocol: 'http'
  }
};

const eventDescription = {
    title: '"""+stock+"""',
    description: 'My first sample market.',
    resolutionDate: resolutionDate.toISOString(),
    outcomes: ['Yes', 'No'],
};

let gnosisInstance;
let ipfsHash;
let oracle;
let categoricalEvent;
let market;

Gnosis.create(options)
.then(result => {
    gnosisInstance = result;
    console.info('[GnosisJS] > connection established');
    console.info("[GnosisJS] > Creating event description...");
    gnosisInstance.publishEventDescription(eventDescription)
    .then(result => {
      ipfsHash = result;
      console.info("[GnosisJS] > Event description hash: " + ipfsHash);
      console.info("[GnosisJS] > Creating Centralized Oracle...");
      gnosisInstance.createCentralizedOracle(ipfsHash)
      .then(result => {
        oracle = result;
        console.info("[GnosisJS] > Centralized Oracle was created");
        console.info("[GnosisJS] > Creating Categorical Event...");
        gnosisInstance.createCategoricalEvent({
            collateralToken: gnosisInstance.etherToken,
            oracle,
            // Note the outcomeCount must match the length of the outcomes array published on IPFS
            outcomeCount: 2,
        })
        .then(result => {
          categoricalEvent = result;
          console.info("[GnosisJS] > Categorical event was created");
          console.info("[GnosisJS] > Creating market...");
          // console.info(gnosisInstance);
          gnosisInstance.createMarket({
              event: categoricalEvent,
              marketMaker: gnosisInstance.lmsrMarketMaker,
              marketFactory: gnosisInstance.standardMarketFactory,
              fee: 50000
          })
          .then(response => {
            market = response;
            console.info("[GnosisJS] > Market was created");
            Promise.all([
                gnosisInstance.etherToken.deposit({ value: 4e18 }),
                gnosisInstance.etherToken.approve(market.address, 4e18),
                market.fund(4e18)
            ])
            .then(values => {
              console.info("[GnosisJS] > All done!");
            })
            .catch(error => {
              console.warn(error);
            });
          })
          .catch(error => {
            console.warn(error);
          });

        })
        .catch(error => {
          console.warn(error);
        });

      })
      .catch(error => {
        console.warn(error);
      });
    })
    .catch(error => {
      console.warn(error);
    });

})
.catch(error => {
  console.warn('Make sure that Gnosis Development kit is up and running');
});
"""

	with open("temp.js", "w") as f:
		f.write(file_contents)

	subprocess.run(["node", "temp.js"], shell=True, check=True)

	return "Ongoing"






@app.route('/convert_er/<val>/<_to>')
def convert_eth_to_real(val, _to):
	if request.method == 'GET':
		resp = re.get('https://api.coinbase.com/v2/exchange-rates?currency=ETH').json()
		# rate of 1 eth to _from currency
		rate = float(resp["data"]['rates'][_to])
		value = float(val) * rate
		result = {"result": str(value), 'status': 'OK'}
		return jsonify(result)


@app.route('/convert_re/<val>/<_from>')
def convert_real_to_eth(val, _from):
	if request.method == 'GET':
		resp = re.get('https://api.coinbase.com/v2/exchange-rates?currency=ETH').json()
		# rate of 1 eth to _from currency
		rate = float(resp["data"]['rates'][_from])
		value = float(val) * (1/rate)
		result = {"result": str(value), 'status': 'OK'}
		return jsonify(result)


@app.route('/nav/<fa>/<fl>/<os>')
def calculate_nav(fa, fl, os):
	if request.method == 'GET':
		nav = (float(fa) - float(fl)) / float(os)
		return jsonify({"result": str(nav), 'status': 'OK'})


@app.errorhandler(404)
def page_not_found(error):
	return "Not Found"


if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5050))
	if not check_for_tokens():
		exit()
	initialize_kite()
	app.run(host='0.0.0.0', port=port, debug=True)
