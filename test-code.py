# Library Imports
import os
import re
import asyncio
import autogen
from autogen import AssistantAgent, GroupChatManager
from autogen import LLMConfig, ModelClient
from autogen.runtime_logging import logging_enabled
from autogen.doc_utils import export_module
from autogen.agentchat import GroupChat, GroupChatManager
#from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen import cache
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from dotenv import load_dotenv
#autogen.logger.setLevel("ERROR")
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from dotenv import load_dotenv
import streamlit as st

# Variables and Function Definitions

# Load Azure Model parameters
load_dotenv()

model = os.getenv("model")
api_key = os.getenv("api_key")
azure_url = os.getenv("azure_url")
api_version = os.getenv("api_ver")

# Function to extract Full name of agent from the Agent Name
def extract_full_name_from_agent_name(s):
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', s)

# Defining LLM Config List
config_list = [
            {
        "model": model,
        "api_key": api_key,
        "base_url": azure_url,
        "api_type": "azure",
        "api_version": api_version
            }
        ]

# Defining the LLM Model Config
az_model_config = {
        "config_list": config_list,
        "seed": 100,
        "temperature": 0.1
}

# Define list to track agent during Group Chat
agent_seq = ["User"]

# Function to print messages for each agent interaction
def st_print(recipient, messages, sender, config):
    agent_seq.append(recipient.name)
    with st.chat_message(sender.name):
        agent = agent_seq.pop(0)
        st.text(extract_full_name_from_agent_name(agent)+":")
        content = messages[-1]['content']
        st.markdown(content)
    return False, None

# Agent Definitions

# Developer Documentation Agent
dev_doc_agent = AssistantAgent(
    name="DeveloperDocumentationAgent",
    llm_config=az_model_config,
    system_message=(
        "You are the Developer Documentation Agent. You will be passed a docstring."
        "You must develop a technical documentation on it, along with the different technical scenarios it can be used in."
        "For each parameter input to the function, you must mention the different use-cases it can be used in and the different forms it can take."
        "Use the general knowledge available to you and gather as many technical scenarios and technical examples you can collect to describle and explain each technical term present in the docstring."
        "Do not execute code statements, you just are supposed to write about them."
    ),
    code_execution_config={"use_docker": False}
)

# Registering reply to print in UI
dev_doc_agent.register_reply(
    [autogen.Agent, None],
    reply_func=st_print, 
    config={"callback": None},
)

# Executive Summary Agent
exec_sum_agent = AssistantAgent(
    name = "ExecutiveSummaryAgent",
    llm_config= az_model_config,
    system_message= (
        "You are the Executive Summary Agent. You focus on the business value."
        "Focus on the business value and briefly explain what the function is about from the docstring passed to you."
        "Use high-level and jargon-free language to describle what the function does, focusing on the business value, and not on the technical terms or explanations."
    )
)

# Registering reply to print in UI
exec_sum_agent.register_reply(
    [autogen.Agent, None],
    reply_func=st_print, 
    config={"callback": None},
)

# API User Guide Agent
api_user_guide_agent = AssistantAgent(
    name = "ApiUserGuideAgent",
    llm_config= az_model_config,
    system_message= (
        "You are the API User Guide Agent."
        "You will be passed a docstring, create example scenarios and practical 'how-to' guide with codes for the users of the function."
        "First focus on the main scenarios and usecases of the function and mention them with examples."
        "Then, focus on the cases around these, slowly moving into the edge and corner cases."
        "Ensure that you cover and create all possible scenarios and examples where the function can be used, including the edge and corner cases."
    )
)

# Registering reply to print in UI
api_user_guide_agent.register_reply(
    [autogen.Agent, None],
    reply_func=st_print, 
    config={"callback": None},
)

# Agents list Definition
agents = [dev_doc_agent, exec_sum_agent, api_user_guide_agent]

# System message
manager_system_message = (
    "You are the Group Chat Manager. You are responsible for managing the conversation between the three agents: The Developer Documentation Agent, the Executive Summary Agent and the API User Guide Agent."
    "Conduct and orchestrate the group chat, ensuring that each of the three agents are called exactly once."
    "You must ensure that you receive a detailed and clear documentation/summary/report from each of the three agents from the conversation."
    "Order of agent calls doesn't matter, but ensure that each agent gets exactly one chance to participate in the group chat."
    "As soon as you receive output from all the three agents, terminate the chat."
)

# Group Chat Manager Description
description_manager = (
    "The group chat manager agent - this agent should be the first to engage when given a new task."
)

# Group Chat Definition
groupchat = autogen.GroupChat(
    agents=agents,
    messages=[],
    allow_repeat_speaker=False,
    max_round=4,
)
 
# Group Chat Manager Definition
manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=az_model_config,
    system_message=manager_system_message,
    description=description_manager,
    is_termination_msg=lambda x: x.get("content", "").strip().endswith("TERMINATE")
)

async def main():

    # Streamlit Configurations

    # Title of Streamlit
    st.title(":arrow_forward: :rainbow[Multi-Agent System for Persona-Driven Technical Documentation]:arrow_backward:")

    # Markdown statements on Streamlit
    st.markdown("""***This app generates tailored documentation for three different personas:  
                :globe_with_meridians: :orange[Developer Documentation Agent] 
                :globe_with_meridians: :blue[Executive Summary Agent] 
                :globe_with_meridians: :violet[API User Guide Agent.]***""")

    st.markdown("***Enter the :green[docstring] of your function and watch the explanations in :green[three different perspectives] unleash!***")

    # Docstring Subheader Section
    st.subheader("Enter your docstring in this section:")

    user_input = st.text_input("Enter your docstring:")

    #user_query = str(input("Enter your docstring:"))

    # Streamlit button
    if st.button("Submit"):

        # Documentations Section
        st.subheader("Persona-driven Documentations Section:")

        # Streamlit 'Info' Statement to initiate chat
        st.info("Initiating Group Chat...")

        # Chat Initiation
        await api_user_guide_agent.a_initiate_chat(
                    manager,
                    message={
                        "role": "user",
                        "content": user_input
                    },
                clear_history = False,
                max_turns=1
                )

        # Print last agent's message alone, as it is not printed as part of the reply function output     
        last_agent = manager.groupchat.messages[-1].get("name", "")
        with st.chat_message("C"):
            st.text(extract_full_name_from_agent_name(last_agent))
            st.write(manager.groupchat.messages[-1].get("content", ""))

        st.subheader("**:green[Group Chat Completed!]**")

# Python file's initial call
if __name__ == "__main__":
    asyncio.run(main())