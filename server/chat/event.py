from chat.eventType import EventType
from datetime import datetime
import json
import uuid
from chat.eventType import agentMap
from chat.multiAgent import get_agent_response
import threading
import time
import random

AGENT_COUNT = 8
CHAT_PATH = "chat/chat_history.json"
agentState = {}

lock = threading.Lock()
chat_history = []
agent_history = []
agentResponse = 0
agentResponseFlag = True
thread = None

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
    global lock, agentResponse, chat_history, agentResponseFlag
    # count = random.randint(0, 2)
    while True:
        # if count > 5:
        #     agentResponseFlag = False
        #     return
        response, agent = get_agent_response(chat_history + agent_history, agentState)
        if not agentState[agent]:
            while True:
                response, agent = get_agent_response(chat_history + agent_history, agentState)
                if agentState[agent]:
                    break
        # print("agent:", agent, ", response: ", response)
        
        with lock:
            if 'human' in agent:
                agentResponseFlag = False
                return
            
            agentResponse += 1
            agent_history.append({
                'speaker': agent,
                'message': response,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'id': str(uuid.uuid4())
            })
        # count += 1
        

def updateChatHistory(input, speaker, recording=False):
    global lock, agentResponse, chat_history, agent_history, agentResponseFlag, thread
    
    if input != '':
        # human speak
        chat_history.append({
                'speaker': speaker,
                'message': input,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'id': str(uuid.uuid4())
            })
        if recording:
            return True
        response, agent = get_agent_response(chat_history, agentState)
        # make sure at lease one agent response
        if 'human' in agent:
            while True:
                response, agent = get_agent_response(chat_history, agentState)
                if agentState[agent] and 'human' not in agent:
                    break
        # agent response
        chat_history.append({
                'speaker': agent,
                'message': response,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'id': str(uuid.uuid4())
            })
        agentResponse = 0
        agentResponseFlag = True
        agent_history = []
        if thread == None or thread.is_alive() == False:
            thread = threading.Thread(target=threadGetResponse)
            thread.start()
    else:
        count = 0
        while agentResponse == 0:
            if thread == None or (thread != None and not thread.is_alive()):
                return False
            if agentResponseFlag == False or count > 5:
                return False
            count += 1
            time.sleep(1)
        with lock:
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

def getAgentState(agent):
    return agentState[agent]

if __name__ == '__main__':
    print(getChatHistory())
    # updateChatHistory("Hello", EventType.USER_INPUT)
    # updateChatHistory("Hi", EventType.AGENT_INPUT)
    # updateChatHistory("How are you?", EventType.USER_INPUT)
    # updateChatHistory("I am fine", EventType.AGENT_INPUT)
    # updateChatHistory("Goodbye", EventType.USER_INPUT)
    # updateChatHistory("Bye", EventType.AGENT_INPUT)
    # print(getChatHistory())