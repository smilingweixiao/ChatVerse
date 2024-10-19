from chat.eventType import EventType
from datetime import datetime
import json
import uuid
from chat.eventType import agentMap

AGENT_COUNT = 8
CHAT_PATH = "server/chat/chat_history.json"
agentState = {}

chat_history = []

def loadChatHistory():
    global chat_history
    try:
        with open(CHAT_PATH, "r") as f:
            chat_history = json.load(f)
    except FileNotFoundError:
        chat_history = []

def initAgentState():
    global agentState
    for agent in agentMap.values():
        agentState[agent] = False

def updateChatHistory(input, eventType):
    response = ""
    if eventType == EventType.USER_INPUT:
        print("Receive user input")
        # response = agentManager(input, agentState)
        response = input
    elif eventType == EventType.AGENT_INPUT:
        print("Receive agent input")
        response = input

    # update chat history
    chat_history.append({
        'speaker': 'user' if eventType == EventType.USER_INPUT else 'agent',
        'message': response,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'id': str(uuid.uuid4())
    })

    # print("Chat history: ", chat_history)
    with open(CHAT_PATH, "w") as f:
        json.dump(chat_history, f, indent=4)

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
    updateChatHistory("Hello", EventType.USER_INPUT)
    updateChatHistory("Hi", EventType.AGENT_INPUT)
    updateChatHistory("How are you?", EventType.USER_INPUT)
    updateChatHistory("I am fine", EventType.AGENT_INPUT)
    updateChatHistory("Goodbye", EventType.USER_INPUT)
    updateChatHistory("Bye", EventType.AGENT_INPUT)
    # print(getChatHistory())