# event.py
import sys
sys.path.append('/Users/victorchen/Desktop/MCHackthon2024_Logi06/server/')
from chat.eventType import EventType
from datetime import datetime
import json
import uuid
from chat.eventType import agentMap
from multiAgent import get_agent_response

AGENT_COUNT = 8
CHAT_PATH = "/Users/victorchen/Desktop/MCHackthon2024_Logi06/server/chat/chat_history.json"
agentState = {}

chat_history = []

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

def updateChatHistory(input_text, eventType, speaker):
    # Update chat history
    chat_history.append({
        'speaker': speaker,
        'message': input_text,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'id': str(uuid.uuid4())
    })

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

def main():
    # Initialize agent states
    selected_roles = {
        "joy": False,
        "debater": True,
        "hater": False,
        "joker": False,
        "thinker": True,
        "nova": True,
        "expert": False,
        "evil": True
    }
    initAgentState(selected_roles)
    loadChatHistory()

    # Start the chat with an initial message
    initial_message = "I am developing a note-taking app, and I want to ask your opinion on names."
    print(f"Human: {initial_message}")
    updateChatHistory(initial_message, EventType.USER_INPUT, 'human')

    try:
        while True:
            user_input = input("Human: ")
            if user_input.lower() == 'exit':
                print("Exiting the chat.")
                break

            # Update chat history with user input
            updateChatHistory(user_input, EventType.USER_INPUT, 'human')

            # Get agent response
            agent_response, speaker = get_agent_response(chat_history, agentState)

            # Print agent response
            print(f"Agent: {agent_response}")

            # Update chat history with agent response
            updateChatHistory(agent_response, EventType.AGENT_INPUT, speaker)

    except KeyboardInterrupt:
        print("\nChat interrupted. Exiting.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("The chat will now exit. Please check your configuration and try again.")

if __name__ == '__main__':
    main()
