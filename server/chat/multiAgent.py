# multiAgent.py

import autogen
import os
from dotenv import load_dotenv
import openai
import random
from typing import List, Dict
from autogen import Agent
import openai.cli

load_dotenv()

api_key = os.environ["OPENAI_API_KEY"]

# Set the API key for OpenAI
openai.api_key = api_key

llm_config = {
    "config_list": [{"model": "gpt-4o-mini", "api_key": api_key}],
}

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

GENERAL_RULES = "You Should Respond BRIEFLY, Speak ORAL Language!!!"

def get_enabled_agents(agentState: Dict[str, bool]) -> List[str]:
    """Return a list of agent names that are enabled to speak (where the value is True)."""
    return [agent for agent, enabled in agentState.items() if enabled]

def initialize_agents(agentState: Dict[str, bool]) -> Dict[str, Agent]:
    # Define new personalities for the chat room with valid names
    agents = {}

    agents['joy'] = autogen.AssistantAgent(
        name="joy",
        system_message="""I am here to make everyone feel welcome! I love to offer support and encouragement in a positive tone.""" + GENERAL_RULES,
        llm_config=gpt4_config,
    )

    agents['debater'] = autogen.AssistantAgent(
        name="debater",
        system_message="""Aggressive Debater. My goal is to challenge your thinking aggressively by considering multiple perspectives and prompting reasoned responses.""" + GENERAL_RULES,
        llm_config=gpt4_config,
    )

    agents['joker'] = autogen.AssistantAgent(
        name="joker",
        system_message="""Jokester. I love telling jokes and making people laugh! My responses will always include a bit of humor, even if it's a little cheesy.""" + GENERAL_RULES,
        llm_config=gpt4_config,
    )

    agents['thinker'] = autogen.AssistantAgent(
        name="thinker",
        system_message="""Critical Thinker. I ask challenging questions, look for flaws in reasoning. My goal is to ensure that every concept is critically evaluated from all angles, leaving no stone unturned.""" + GENERAL_RULES,
        llm_config=gpt4_config,
    )

    agents['nova'] = autogen.AssistantAgent(
        name="nova",
        system_message="""Creative Muse. I am all about imagination and creativity. I love suggesting out-of-the-box ideas and approaches. My responses will help you think in novel and inventive ways.""" + GENERAL_RULES,
        llm_config=gpt4_config,
    )

    agents['expert'] = autogen.AssistantAgent(
        name="expert",
        system_message="""Knowledge Expert. I specialize in providing accurate and in-depth information on a variety of topics. My goal is to provide examples or analogies.""" + GENERAL_RULES,
        llm_config=gpt4_config,
    )

    agents['hater'] = autogen.AssistantAgent(
        name="hater",
        system_message="""Relentless Critic. I am here to poke holes in every idea, point out every flaw, and be your HARSHEST critic. My goal is to show you the weaknesses in your thinking and push you to defend your ideas against tough scrutiny.""" + GENERAL_RULES,
        llm_config=gpt4_config,
    )

    agents['evil'] = autogen.AssistantAgent(
        name="evil",
        system_message="""You like to sail close to the wind, try to come up with some evil ideas, and let others know that there are problems with their ideas.""" + GENERAL_RULES,
        llm_config=gpt4_config,
    )

    # Filter agents based on agentState
    enabled_agents = {name: agent for name, agent in agents.items() if agentState.get(name, False)}
    return enabled_agents

def call_llm_api(conversation_history: str, enabled_agents: List[str]) -> str:
    """Send the conversation history to the LLM and get the suggested next speaker."""
    try:
        agent_names = ', '.join(enabled_agents)
        # print("The following is the conversaiton: ")
        # print(conversation_history)
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Determine which agent should respond next based on the conversation."},
                {"role": "user", "content": f"Given the following conversation, who should speak next, the following is their names: human, {agent_names}? Just answer who should be fine.\n\n{conversation_history}"}
            ],
            max_tokens=50,
            temperature=0.7,
        )
        # Extract the suggestion from the response
        suggestion = response.choices[0].message.content.strip()
        return suggestion
    except Exception as e:
        print(f"An error occurred when calling the LLM API: {str(e)}")
        # Fallback to a random agent if the LLM call fails
        return random.choice(["human"] + enabled_agents)

def generate_response_with_references(agent: Agent, conversation_history: str, last_message: str) -> str:
    """Generate a response that may include a reference to another agent's message."""
    try:
        # Use LLM to generate a response that might reference previous speakers
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"{agent.name}. You should respond to the conversation. You can refer to previous messages from other agents."},
                {"role": "user", "content": f"Conversation history:\n{conversation_history}\n\nRespond to the last message: '{last_message}'"}
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

def get_agent_response(chat_history: List[Dict], agentState: Dict[str, bool]) -> str:
    """Process the chat history and return the agent's response."""
    # Initialize agents
    enabled_agents = get_enabled_agents(agentState)
    agents = initialize_agents(agentState)

    if not enabled_agents:
        return "No agents are enabled to respond."

    # Parse chat history into conversation history format
    conversation_history = "\n".join([f"{msg['speaker']}: {msg['message']}" for msg in chat_history])

    # Determine the next speaker
    suggested_speaker = call_llm_api(conversation_history, enabled_agents)

    print("Suggestion: ", suggested_speaker)

    # Map the suggested speaker to the agent
    agent = None
    for name in enabled_agents:
        if name.lower() in suggested_speaker.lower():
            agent = agents[name]
            break

    if not agent:
        # Fallback to a random enabled agent
        agent = agents[random.choice(enabled_agents)]

    # Get the last message
    last_message = chat_history[-1]['message'] if chat_history else ""

    # Generate the agent's response
    response_text = generate_response_with_references(agent, conversation_history, last_message)

    return response_text, suggested_speaker
