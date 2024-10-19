from chat.eventType import EventType
from datetime import datetime
import json
import uuid
from chat.eventType import agentMap
from chat.multiAgent import get_agent_response
import threading
import time

AGENT_COUNT = 8
CHAT_PATH = "server/chat/chat_history.json"
agentState = {}

lock = threading.Lock()
chat_history = []
agent_history = []
agentResponse = 0

def loadChatHistory():
    global chat_history
    try:
        with open(CHAT_PATH, "r") as f:
            chat_history = json.load(f)
    except FileNotFoundError:
        chat_history = []

def initAgentState(initial_state=None):
    global agentState
    for agent in agentMap.values():
        if initial_state and agent in initial_state:
            agentState[agent] = initial_state[agent]
        else:
            agentState[agent] = False

def threadGetResponse():
    global lock, agentResponse, chat_history
    while True:
        agent_response, agent = get_agent_response(chat_history + agent_history, agentState)
        print("agent:", agent, ", response: ", agent_response)
        if len(agent_response.split("\n\n")) > 1:
                parts = agent_response.split("\n\n")
                print(f'parts: {parts}')
                try:
                    name1, text1 = parts[0].split(": ", 1)
                    name2, text2 = parts[1].split(": ", 1)
                    # updateChatHistory(text1, EventType.AGENT_INPUT, name1)
                    # updateChatHistory(text2, EventType.AGENT_INPUT, name2)
                    chat_history.append({
                        'speaker': name1,
                        'message': text1,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'id': str(uuid.uuid4())
                    })
                    chat_history.append({
                        'speaker': name2,
                        'message': text2,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'id': str(uuid.uuid4())
                    })
                    print(f'{name1}: {text1}')
                    print(f'{name2}: {text2}')
                except:
                    name = agent
                    text = agent_response
                    chat_history.append({
                        'speaker': agent,
                        'message': agent_response,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'id': str(uuid.uuid4())
                    })
        else:
            if ": " in agent_response:
                name, text = agent_response.split(": ", 1)
                # updateChatHistory(text, EventType.AGENT_INPUT, name)
                chat_history.append({
                    'speaker': name,
                    'message': text,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'id': str(uuid.uuid4())
                })
                print(f'{name}: {text}')
            else:
                # updateChatHistory(agent_response, EventType.AGENT_INPUT, speaker)
                chat_history.append({
                    'speaker': agent,
                    'message': agent_response,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'id': str(uuid.uuid4())
                })
                print(f'{agent}: {agent_response}')
        with lock:
            agentResponse += 1
            agent_history.append({
                'speaker': agent,
                'message': agent_response,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'id': str(uuid.uuid4())
            })
            if agent_response == 'should respond next: human' or agent == 'human':
                agentResponse = -1
                return
        

def updateChatHistory(input, speaker):
    global lock, agentResponse, chat_history
    
    if speaker == 'human':
        chat_history.append({
                'speaker': speaker,
                'message': input,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'id': str(uuid.uuid4())
            })
        # print("Receive user input")
        agent_response, agent = get_agent_response(chat_history, agentState)
        if len(agent_response.split("\n\n")) > 1:
                parts = agent_response.split("\n\n")
                print(f'parts: {parts}')
                try:
                    name1, text1 = parts[0].split(": ", 1)
                    name2, text2 = parts[1].split(": ", 1)
                    # updateChatHistory(text1, EventType.AGENT_INPUT, name1)
                    # updateChatHistory(text2, EventType.AGENT_INPUT, name2)
                    chat_history.append({
                        'speaker': name1,
                        'message': text1,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'id': str(uuid.uuid4())
                    })
                    chat_history.append({
                        'speaker': name2,
                        'message': text2,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'id': str(uuid.uuid4())
                    })
                    print(f'{name1}: {text1}')
                    print(f'{name2}: {text2}')
                except:
                    name = agent
                    text = agent_response
                    chat_history.append({
                        'speaker': agent,
                        'message': agent_response,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'id': str(uuid.uuid4())
                    })
        else:
            if ": " in agent_response:
                name, text = agent_response.split(": ", 1)
                # updateChatHistory(text, EventType.AGENT_INPUT, name)
                chat_history.append({
                    'speaker': name,
                    'message': text,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'id': str(uuid.uuid4())
                })
                print(f'{name}: {text}')
            else:
                # updateChatHistory(agent_response, EventType.AGENT_INPUT, speaker)
                chat_history.append({
                    'speaker': agent,
                    'message': agent_response,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'id': str(uuid.uuid4())
                })
                print(f'{agent}: {agent_response}')
        agentResponse = 0
        thread = threading.Thread(target=threadGetResponse)
        thread.start()
    elif speaker == '':
        # print("Get agent input")
        count = 0
        while agentResponse == 0:
            # print("Waiting for agent response, agentResponse: ", agentResponse)
            if agentResponse == -1 or count > 20:
                return False
            count += 1
            time.sleep(1)
        # print("Waiting for agentResponse's lock")
        with lock:
            # print("agentResponse's lock acquired, agentResponse: ", agentResponse)
            agentResponse -= 1
            message = agent_history.pop(0)
        if message['speaker'] == 'human':
            return False
        chat_history.append(message)

    with open(CHAT_PATH, "w") as f:
        json.dump(chat_history, f, indent=4)
    
    return True

def getChatHistory():
    return chat_history

def clearChatHistory():
    global chat_history
    chat_history = []
    with open(CHAT_PATH, "w") as f:
        json.dump(chat_history, f, indent=4)

def toggleAgent(agent):
    agentState[agent] = not agentState[agent]
    print(agentState)

if __name__ == '__main__':
    print(getChatHistory())
    # updateChatHistory("Hello", EventType.USER_INPUT)
    # updateChatHistory("Hi", EventType.AGENT_INPUT)
    # updateChatHistory("How are you?", EventType.USER_INPUT)
    # updateChatHistory("I am fine", EventType.AGENT_INPUT)
    # updateChatHistory("Goodbye", EventType.USER_INPUT)
    # updateChatHistory("Bye", EventType.AGENT_INPUT)
    # print(getChatHistory())