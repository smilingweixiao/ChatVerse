import autogen
import json
import os
from dotenv import load_dotenv
import time
import openai
import random

load_dotenv()

api_key = os.environ["OPENAI_API_KEY"]

# Set the API key for OpenAI
openai.api_key = api_key

llm_config = {
    "config_list": [{"model": "gpt-4o-mini", "api_key": api_key}],
}

# Assuming you have 'oai_config.json' properly set up, else you can skip this
config_list = autogen.config_list_from_json(
    env_or_file="./server/chat/oai_config.json",
    filter_dict={
        "model": ["gpt-4o-mini"],
    },
)

gpt4_config = {
    "config_list": config_list,
    "timeout": 120,
}

GENERAL_RULES = "You should respond briefly and speak in casual, conversational language."

# Define assistant agents with their personalities
joy = autogen.AssistantAgent(
    name="joy",
    system_message=(
        "I am here to make everyone feel welcome! "
        "I love to offer support and encouragement in a positive tone."
        + GENERAL_RULES
    ),
    llm_config=gpt4_config,
)

debater = autogen.AssistantAgent(
    name="debater",
    system_message=(
        "Aggressive Debater. My goal is to challenge your thinking aggressively by considering multiple perspectives and prompting reasoned responses."
        + GENERAL_RULES
    ),
    llm_config=gpt4_config,
)

joker = autogen.AssistantAgent(
    name="joker",
    system_message=(
        "Jokester. I love telling jokes and making people laugh! My responses will always include a bit of humor, even if it's a little cheesy."
        + GENERAL_RULES
    ),
    llm_config=gpt4_config,
)

thinker = autogen.AssistantAgent(
    name="thinker",
    system_message=(
        "Critical Thinker. I ask challenging questions, look for flaws in reasoning. "
        "My goal is to ensure that every concept is critically evaluated from all angles, leaving no stone unturned."
        + GENERAL_RULES
    ),
    llm_config=gpt4_config,
)

nova = autogen.AssistantAgent(
    name="nova",
    system_message=(
        "Creative Muse. I am all about imagination and creativity. "
        "I love suggesting out-of-the-box ideas and approaches. "
        "My responses will help you think in novel and inventive ways."
        + GENERAL_RULES
    ),
    llm_config=gpt4_config,
)

expert = autogen.AssistantAgent(
    name="expert",
    system_message=(
        "Knowledge Expert. I specialize in providing accurate and in-depth information on a variety of topics. "
        "My goal is to provide examples or analogies."
        + GENERAL_RULES
    ),
    llm_config=gpt4_config,
)

hater = autogen.AssistantAgent(
    name="hater",
    system_message=(
        "Relentless Critic. I am here to poke holes in every idea, point out every flaw, and be your harshest critic. "
        "My goal is to show you the weaknesses in your thinking and push you to defend your ideas against tough scrutiny."
        + GENERAL_RULES
    ),
    llm_config=gpt4_config,
)

evil = autogen.AssistantAgent(
    name="evil",
    system_message=(
        "You like to sail close to the wind, try to come up with some evil ideas, and let others know that there are problems with their ideas."
        + GENERAL_RULES
    ),
    llm_config=gpt4_config,
)

user_proxy = autogen.UserProxyAgent(
    name="human",
    system_message="A human user interacting with the group chat.",
    human_input_mode="ALWAYS",
)

from typing import Dict, List
from autogen import Agent

# Initialize the group chat globally
groupchat = autogen.GroupChat(
    agents=[],
    messages=[],
    max_round=20,
    speaker_selection_method=None,  # Will be set later
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

def call_llm_api(conversation_history: str) -> str:
    """Send the conversation history to the LLM and get the suggested next speaker."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Determine which agent should respond next based on the conversation."},
                {
                    "role": "user",
                    "content": (
                        "Given the following conversation, who should speak next: human, joy, debater, hater, joker, thinker, nova, expert, evil? "
                        "Just answer with the name of the agent.\n\n" + conversation_history
                    ),
                },
            ],
            max_tokens=10,
            temperature=0.7,
        )
        # Extract the suggestion from the response
        suggestion = response.choices[0].message.content.strip()
        return suggestion
    except Exception as e:
        print(f"An error occurred when calling the LLM API: {str(e)}")
        # Fallback to a random agent if the LLM call fails
        return random.choice(
            ["human", "joy", "debater", "hater", "joker", "thinker", "nova", "expert", "evil"]
        )

def generate_response_with_references(agent: Agent, conversation_history: str, last_message: str) -> str:
    """Generate a response from the agent to the last message, without including messages from other speakers."""
    try:
        # Use LLM to generate a response that might reference previous messages
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are {agent.name}, an assistant in a group chat. "
                        "Respond to the last message appropriately, speaking as yourself. "
                        "Do not include other speakers' messages in your response."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Conversation history:\n{conversation_history}\n\n"
                        f"The last message was: '{last_message}'. What is your reply?"
                    ),
                },
            ],
            max_tokens=150,
            temperature=0.7,
        )
        # Extract the response content
        response_text = response.choices[0].message.content.strip()
        return response_text
    except Exception as e:
        print(f"An error occurred while generating a response with references: {str(e)}")
        return f"{agent.name} is having some technical difficulties responding right now."

def custom_speaker_selection_func(last_speaker: Agent, groupchat: autogen.GroupChat):
    """Determine the next speaker using LLM suggestions based on the conversation history."""
    # Get the conversation history as text
    conversation_history = "\n".join([f"{msg['name']}: {msg['content']}" for msg in groupchat.messages])

    # Use the LLM to determine the next speaker
    suggested_speaker = call_llm_api(conversation_history)

    print("Suggestion from LLM for next speaker:", suggested_speaker)

    # Map the LLM suggestion to the correct agent
    agent_mapping = {
        "joy": joy,
        "debater": debater,
        "hater": hater,
        "joker": joker,
        "thinker": thinker,
        "nova": nova,
        "expert": expert,
        "evil": evil,
        "human": user_proxy,
    }

    for name, agent in agent_mapping.items():
        if name.lower() == suggested_speaker.strip().lower():
            return agent

    # Fallback to a random agent if the LLM suggestion is unclear
    return random.choice(groupchat.agents)

def get_agent_response(chat_history, agent_state):
    """
    Generate the next agent response based on the chat history and agent states.

    Parameters:
    - chat_history: a list of dictionaries, each with keys 'speaker', 'message'
    - agent_state: a dictionary mapping agent names to a boolean indicating whether they are active

    Returns:
    - response: the generated response
    - agent_name: the name of the agent who generated the response
    """
    # Reconstruct groupchat.messages from chat_history
    # print('agent_state:', agent_state)
    groupchat.messages = [
        {'name': entry['speaker'], 'content': entry['message'], 'role': 'user'} for entry in chat_history
    ]

    # Build a list of active agents
    active_agent_names = [name for name, active in agent_state.items() if active]
    all_agents = [joy, debater, hater, joker, thinker, nova, expert, evil, user_proxy]
    active_agents = [agent for agent in all_agents if agent.name in active_agent_names]

    if not active_agents:
        # If no agents are active, return None
        return "", "No active agents"

    # Set the agents in the groupchat to active agents
    groupchat.agents = active_agents

    # Set the speaker selection method
    groupchat.speaker_selection_method = custom_speaker_selection_func

    # Get the last speaker
    last_speaker_name = chat_history[-1]['speaker'] if chat_history else None
    last_speaker = next((agent for agent in groupchat.agents if agent.name == last_speaker_name), None)

    # Determine the next speaker
    next_speaker = custom_speaker_selection_func(last_speaker, groupchat)

    # If the next speaker is 'human', return None for response
    if next_speaker.name == 'human':
        print("Next speaker is human!")
        return '', 'human'

    # Generate the response
    conversation_history = "\n".join([f"{msg['name']}: {msg['content']}" for msg in groupchat.messages])
    last_message = groupchat.messages[-1]['content'] if groupchat.messages else ''
    response_text = generate_response_with_references(next_speaker, conversation_history, last_message)
    print(f"Response from {next_speaker.name}: {response_text}")
    return response_text, next_speaker.name
