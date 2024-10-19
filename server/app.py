from flask import Flask, request, jsonify
from flask_cors import CORS
# import json
# import requests
# import os
# import sys

recording = False

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/start_recording', methods=['POST'])
def startRecord():
    global recording
    if recording:
        return jsonify({'message': 'Recording already in progress'}), 400
    recording = True
    from audio.record import startRecording
    startRecording()
    return jsonify({'message': 'Recording started'}), 200

@app.route('/api/stop_recording', methods=['POST'])
def stopRecord():
    global recording
    if not recording:
        return jsonify({'message': 'No recording in progress'}), 400
    recording = False
    from audio.record import stopRecording
    stopRecording()+
    return jsonify({'message': 'Recording completed'}), 200

if __name__ == '__main__':
    
    app.run(host='127.0.0.1', port=5000)