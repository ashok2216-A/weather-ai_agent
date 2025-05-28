from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
import os
from agent import create_agent

# Load environment variables and initialize session state
load_dotenv()

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mistral_api_key" not in st.session_state:
    st.session_state.mistral_api_key = os.getenv("MISTRAL_API_KEY", "")
if "agent" not in st.session_state:
    st.session_state.agent = None

# Page configuration
st.set_page_config(page_title="AI Assistant", page_icon="🤖")

# Basic styling
st.markdown("""
<style>
    .chat-message { 
        padding: 1rem; 
        border-radius: 10px; 
        margin-bottom: 1rem; 
    }
    .success-message {
        color: #155724;
        background-color: #d4edda;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🤖 AI Assistant")
    st.markdown("---")
    
    # API Key input
    api_key_input = st.text_input(
        "🔑 Mistral AI API Key", value=st.session_state.mistral_api_key, type="password", help="Get your API key from: https://console.mistral.ai")
    
    if api_key_input != st.session_state.mistral_api_key:
        st.session_state.mistral_api_key = api_key_input
        st.session_state.agent = None
        st.rerun()
    
    # Available Features section
    st.markdown("---")
    st.markdown("### 🔧 Available Features")
    st.markdown("""
    **Time Services:**
    - 🌍 Current time in any timezone
    - 🕐 Support for common abbreviations
    
    **Weather Services:**  
    - 🌤️ Current weather conditions
    - 🌡️ Temperature information
    """)
    
    # Clear Chat button
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.title("💬 AI Agent")

# Check for API key
if not st.session_state.mistral_api_key:
    st.warning("⚠️ Please enter your Mistral API key in the sidebar to start chatting.")
    st.stop()

# Initialize agent if needed
if not st.session_state.agent and st.session_state.mistral_api_key:
    with st.spinner("🚀 Initializing AI Assistant..."):
        try:
            st.session_state.agent = create_agent(st.session_state.mistral_api_key)
        except Exception as e:
            st.error(f"Error initializing agent: {str(e)}")
            st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about time or weather..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                response = st.session_state.agent.run(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {str(e)}")
