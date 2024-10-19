from flask import Flask, request, jsonify
from flask_cors import CORS
# from flask_socketio import SocketIO
import chat.event as event
from chat.eventType import EventType, agentMap

recording = False

app = Flask(__name__)
# CORS(app)
# socketio = SocketIO(app)

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
    stopRecording()
    return jsonify(event.getChatHistory()[-1]), 200

@app.route('/api/chat', methods=['GET', 'POST', 'DELETE'])
def chat():
    if request.method == 'GET':
        return jsonify(event.getChatHistory()), 200
    elif request.method == 'POST':
        data = request.json
        status = event.updateChatHistory(data.get('message'), data.get('speaker'))
        if status:
            return jsonify(event.getChatHistory()[-1]), 200
        else:
            return jsonify({
                'speaker': '',
                'message': '',
                'timestamp': '',
                'id': ''
                }), 200
    else:
        event.clearChatHistory()
        return jsonify({'message': 'Chat history cleared'}), 200

@app.route('/api/console/<int:agent_id>', methods=['GET'])
def toggleAgent1(agent_id):
    agent = agentMap[agent_id]
    event.toggleAgent(agent)
    
    socketio.emit('role_updated', agent)
    return jsonify({'message': f'Agent {agent} toggled'}), 200

if __name__ == '__main__':
    event.loadChatHistory()
    event.initAgentState({
        "joy": True,
        "debater": True,
        "hater": True,
        "joker": True,
        "thinker": True,
        "nova": True,
        "expert": False,
        "evil": False
    })
    app.run(host='127.0.0.1', port=5000)