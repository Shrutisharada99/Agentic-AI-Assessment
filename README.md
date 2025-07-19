Multi-Agent System for Persona-Driven Technical Documentation 
--------------------------------------------------------------

This repository consists of **Autogen + Streamlit + Deploy** code and Use Case Document of an autonomous multi-agent system that takes a single source of truth - **a Python function's docstring.**
It generates tailored documentations for three different personas:
1. **Developer Documentation Agent**
2. **Executive Summary Agent**
3. **API User Guide Agent**

The app is deplyed and can be readily used at: https://agentic-ai-assessment-autogen-multi-agents.streamlit.app/

Contents of repository:

1. **streamlit_deploy folder**: With main 'stream_docs.py' code that can be run on Streamlit and the requirements.txt file.
2. **.streamlit/sample_secrets.toml file** - Sample file to store secret variables to use in local enviroment for testing before deploying into Streamlit.
3. **Use case Document** that consists of the problem statement, technical design and architecture and the system prompts engineered for the different agents in the multi-agent flow.
