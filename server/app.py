from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import chat.event as event
from chat.eventType import EventType, agentMap
import logging

recording = False

app = Flask(__name__)
# 配置CORS
socketio = SocketIO(app, cors_allowed_origins="http://127.0.0.1:3000")

CORS(app)

# 配置SocketIO
# socketio = SocketIO(app)



logging.basicConfig(level=logging.INFO)

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
    state = event.getAgentState(agent)
    
    socketio.emit('role_updated', {'roleName': agent, 'roleState': state})
    # emit('role_updated', 'roleName: ' + agent, broadcast=True)
    # socketio.emit('role_updated', {'roleName': agent})
    return jsonify({'message': f'Agent {agent} toggled'}), 200

@socketio.on('connect')
def handle_connect():
    print("A client connected!")  # 客戶端連接時觸發
    
@socketio.on('disconnect')
def handle_disconnect():
    print("A client disconnected!")  # 客戶端連接時觸發
    
# @socketio.on('role_updated')
# def handle_message(data):
#     print('Received message:', data)
#     return 'Role updated!'

if __name__ == '__main__':
    # event.loadChatHistory()
    event.initAgentState({
        "joy": False,
        "debater": False,
        "hater": False,
        "joker": False,
        "thinker": False,
        "nova": False,
        "expert": False,
        "evil": False
    })
    socketio.run(app, host='localhost', port=5000)