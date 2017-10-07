import requests
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify
import sys
import logging
import os
app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

app.secret_key = 'secret'


@app.route('/')
def index():
	return "Hello World"


@app.errorhandler(404)
def page_not_found(error):
	return "Not Found"


if __name__ == '__main__':
	app.run(debug=True)
