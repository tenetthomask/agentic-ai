import streamlit as st
import ollama
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Ollama Cloud Chat", page_icon="☁️")
st.title("☁️ Ollama Cloud Chatbot")

# Sidebar for API Key and Model Selection
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Ollama API Key", type="password")
    # Cloud models usually end with the '-cloud' suffix
    model_name = st.selectbox(
        "Select Cloud Model", 
        ["gpt-oss:20b-cloud", "gpt-oss:120b-cloud", "qwen3-coder:480b-cloud"]
    )
    st.info("Ensure you are signed in via `ollama signin` on your machine if running locally.")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 2. CHAT LOGIC ---
if prompt := st.chat_input("How can I help you today?"):
    # Check for API Key
    if not api_key:
        st.error("Please enter your Ollama API Key in the sidebar.")
        st.stop()

    # Add user message to state and UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Initialize Cloud Client
    # In 2026, the Client can point directly to the cloud endpoint
    client = ollama.Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {api_key}"}
    )

    # Generate Response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Using streaming for a better UI experience
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