from flask import Flask, request, jsonify
from flask_cors import CORS
# import json
# import requests
# import os
# import sys

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    
    app.run(host='127.0.0.1', port=5000)