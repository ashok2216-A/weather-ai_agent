from datetime import datetime
import requests
import streamlit as st
from dotenv import load_dotenv
import os
from agent import create_agent

# Load environment variables and initialize session state
load_dotenv()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mistral_api_key" not in st.session_state:
    st.session_state.mistral_api_key = os.getenv("MISTRAL_API_KEY", "")

# Page configuration and styling
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")
st.markdown("""
<style>
    .chat-message { padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; }
    .chat-message.user { background-color: #f7f7f8; }
    .chat-message.assistant { background-color: #ffffff; }
    .chat-message .message { margin-left: 30px; }
    .stTextInput { max-width: 500px; }
</style>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.title("🤖 AI Assistant")
    api_key_input = st.text_input(
        "Enter Mistral API Key",
        value=st.session_state.mistral_api_key,
        type="password",
        help="Enter your Mistral AI API key here. Get one from https://console.mistral.ai"
    )
    
    if api_key_input != st.session_state.mistral_api_key:
        st.session_state.mistral_api_key = api_key_input
        st.rerun()

    st.markdown("### 🔧 Capabilities\n- ⏰ Current time\n- 🌤️ Weather information")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Initialize agent
try:
    agent = create_agent(st.session_state.mistral_api_key)
    if not agent:
        st.warning("⚠️ Please enter a valid Mistral API key in the sidebar to start chatting.")
        st.stop()
except Exception as e:
    st.error(f"Error initializing agent: {str(e)}")
    st.stop()

# Main chat interface
st.title("💬 Chat Interface")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input and response
if prompt := st.chat_input("What would you like to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = agent.run(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
