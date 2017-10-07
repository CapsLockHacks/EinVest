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

from .config import KITE_API_KEY, KITE_REQUEST_TOKEN, KITE_SECRET
from .scaffold import *

app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

app.secret_key = 'secret'


# xe.com
xe_account_id = 'student926567212'
xe_api_key = 'a77skb1r13cnrhjg5j8953nuvj'


def initialize_kite():
	"""
	Helper function to initialize Kite.
	"""
	kite = KiteConnect(api_key=KITE_API_KEY)

	try:
		with open(path.join(args.path, 'token.ini'), 'r') as the_file:
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

		with open(path.join(args.path, 'token.ini'), 'w') as the_file:
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


@app.errorhandler(404)
def page_not_found(error):
	return "Not Found"


if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5050))
	app.run(host='0.0.0.0', port=port, debug=True)
