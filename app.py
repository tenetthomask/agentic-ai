import streamlit as st
import ollama
import os
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()
DEFAULT_API_KEY = os.getenv("OLLAMA_API_KEY", "")

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Ollama Cloud Chat", page_icon="☁️")
st.title("☁️ Ollama Cloud Chatbot")

# Sidebar for API Key and Model Selection
with st.sidebar:
    st.header("Settings")
    # The value is now pre-filled from your environment variable
    api_key = st.text_input("Ollama API Key", value=DEFAULT_API_KEY, type="password")
    
    model_name = st.selectbox(
        "Select Cloud Model", 
        ["gpt-oss:20b-cloud", "gpt-oss:120b-cloud", "qwen3-coder:480b-cloud"]
    )
    st.info("API Key loaded from environment.")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 2. CHAT LOGIC ---
if prompt := st.chat_input("How can I help you today?"):
    if not api_key:
        st.error("Please enter your Ollama API Key in the sidebar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = ollama.Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {api_key}"}
    )

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try: # Fixed: added missing colon
            response = client.chat(
                model=model_name,
                messages=st.session_state.messages,
                stream=True,
            )
            
            for chunk in response:
                content = chunk['message']['content']
                full_response += content
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error connecting to Ollama Cloud: {e}")