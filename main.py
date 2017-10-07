import requests as re
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify
import sys
import logging
import os
app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

app.secret_key = 'secret'

# xe.com
xe_account_id = 'student926567212'
xe_api_key = 'a77skb1r13cnrhjg5j8953nuvj'


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
