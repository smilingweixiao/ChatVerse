import autogen
import json
import os
from dotenv import load_dotenv
import time
import openai
import random
from typing import List

load_dotenv()

api_key = os.environ["OPENAI_API_KEY"]

# Set the API key for OpenAI
openai.api_key = api_key

llm_config = {
    "config_list": [{"model": "gpt-4o-mini", "api_key": api_key}],
}

config_list = autogen.config_list_from_json(
    env_or_file="oai_config.json", 
    filter_dict={
        "model": ["gpt-4o-mini"],
    },
)

gpt4_config = {
    "config_list": config_list,
    "timeout": 120,
}

GENERAL_RULES = "You Should Respond BRIVELY, Speack ORAL Language!!!"

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

def get_enabled_agents() -> List[str]:
    """Return a list of agent names that are enabled to speak (where the value is True)."""
    return [agent for agent, enabled in selected_roles.items() if enabled]

# Define new personalities for the chat room with valid names
joy = autogen.AssistantAgent(
    name="joy",
    system_message="""I am here to make everyone feel welcome! I love to offer support and encouragement in a positive tone.""" + GENERAL_RULES,
    llm_config=gpt4_config,
)

debater = autogen.AssistantAgent(
    name="debater",
    system_message="""Aggresive Debater. My goal is to challenge your thinking aggresively by considering multiple perspectives and prompting reasoned responses."""+ GENERAL_RULES,
    llm_config=gpt4_config,
)

joker = autogen.AssistantAgent(
    name="joker",
    system_message="""Jokester. I love telling jokes and making people laugh! My responses will always include a bit of humor, even if it's a little cheesy."""+ GENERAL_RULES,
    llm_config=gpt4_config,
)

thinker = autogen.AssistantAgent(
    name="thinker",
    system_message="""Critical Thinker. I ask challenging questions, look for flaws in reasoning. My goal is to ensure that every concept is critically evaluated from all angles, leaving no stone unturned."""+ GENERAL_RULES,
    llm_config=gpt4_config,
)

nova = autogen.AssistantAgent(
    name="nova",
    system_message="""Creative Muse. I am all about imagination and creativity. I love suggesting out-of-the-box ideas and approaches. My responses will help you think in novel and inventive ways."""+ GENERAL_RULES,
    llm_config=gpt4_config,
)

expert = autogen.AssistantAgent(
    name="expert",
    system_message="""Knowledge Expert. I specialize in providing accurate and in-depth information on a variety of topics. My goal is to provide example or analogy."""+ GENERAL_RULES,
    llm_config=gpt4_config,
)

hater = autogen.AssistantAgent(
    name="hater",
    system_message="""Relentless Critic. I am here to poke holes in every idea, point out every flaw, and be your HARSHEST critic. My goal is to show you the weaknesses in your thinking and push you to defend your ideas against tough scrutiny."""+ GENERAL_RULES,
    llm_config=gpt4_config,
)

evil = autogen.AssistantAgent(
    name="evil",
    system_message="""You like to sail close to the wind, try to come up with some evil ideas, and let others know that there are problems with their ideas."""+ GENERAL_RULES,
    llm_config=gpt4_config,
)

user_proxy = autogen.UserProxyAgent(
    name="Human",
    system_message="A human user interacting with the group chat.",
    human_input_mode="ALWAYS",
)

from typing import Dict, List
from autogen import Agent

def call_llm_api(conversation_history: str) -> str:
    """Send the conversation history to the LLM and get the suggested next speaker."""
    try:
        enabled_agents = get_enabled_agents()
        agent_names = ', '.join(enabled_agents)
        # print(f"Given the following conversation, who should speak next: human, {agent_names}? Just answer who should be fine.\n\n{conversation_history}")

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Determine which agent should respond next based on the conversation."},
                {"role": "user", "content": f"Given the following conversation, who should speak next: human, {agent_names}? Just answer who should be fine.\n\n{conversation_history}"}
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
        return random.choice(["human","joy", "debater", "hater", "joker", "thinker", "nova", "expert", "evil"])

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

def custom_speaker_selection_func(last_speaker: Agent, groupchat: autogen.GroupChat):
    """Determine the next speaker using LLM suggestions based on the conversation history."""
    # Get the conversation history as text
    conversation_history = "\n".join([f"{msg['name']}: {msg['content']}" for msg in groupchat.messages])
    # print(f"Conversation history:\n{conversation_history}\n")

    # Use the LLM to determine the next speaker
    suggested_speaker = call_llm_api(conversation_history)

    print("suggestion: ", suggested_speaker)

    # Map the LLM suggestion to the correct agent
    if "joy" in suggested_speaker.lower():
        return joy
    elif "debater" in suggested_speaker.lower():
        return debater
    elif "hater" in suggested_speaker.lower():
        return hater
    elif "joker" in suggested_speaker.lower():
        return joker
    elif "thinker" in suggested_speaker.lower():
        return thinker
    elif "nova" in suggested_speaker.lower():
        return nova
    elif "expert" in suggested_speaker.lower():
        return expert
    elif "evil" in suggested_speaker.lower():
        return evil
    elif "human" in suggested_speaker.lower():
        return user_proxy
    else:
        # Fallback to a random agent if the LLM suggestion is unclear
        return random.choice([joy, debater, hater, joker, thinker, nova, expert, evil, user_proxy])


# Create a group chat with the new agents
groupchat = autogen.GroupChat(
    agents=[joy, debater, hater, joker, thinker, nova, expert, evil, user_proxy],
    messages=[],
    max_round=20,
    speaker_selection_method=custom_speaker_selection_func,
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

def run_chat():
    # Start the chat with an initial message
    initial_message = "I am developing a note taking app, I want to ask your opion on names."
    print(f"Human: {initial_message}")

    try:
        # Initiate the chat
        user_proxy.initiate_chat(
            manager,
            message=initial_message,
        )

        # Continue the conversation
        while True:
            user_input = input("Human: ")
            if user_input.lower() == 'exit':
                print("Exiting the chat.")
                break

            try:
                # Send the user's message to the group chat
                user_proxy.send(
                    message=user_input,
                    recipient=manager,
                )

                # After user input, determine the next agent's response
                last_speaker = groupchat.agents[-1]
                next_speaker = custom_speaker_selection_func(last_speaker, groupchat)

                # Generate the response with potential references
                conversation_history = "\n".join([f"{msg['name']}: {msg['content']}" for msg in groupchat.messages])
                last_message = groupchat.messages[-1]['content']
                response_text = generate_response_with_references(next_speaker, conversation_history, last_message)

                # Print the next speaker's response
                print(f"{next_speaker.name}: {response_text}")

                # Add the response to the group chat
                groupchat.messages.append({"name": next_speaker.name, "content": response_text, "role": "user"})

            except Exception as e:
                print(f"An error occurred: {str(e)}")
                print("Let's try again. If the error persists, you may want to restart the chat.")
                time.sleep(2)  # Wait for 2 seconds before continuing

    except KeyboardInterrupt:
        print("\nChat interrupted. Exiting.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("The chat will now exit. Please check your configuration and try again.")

if __name__ == "__main__":
    run_chat()