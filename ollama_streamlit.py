import streamlit as st
import ollama
from typing import Dict, Generator
from PIL import Image
import os
import json
import urllib.request

def ollama_generator(model_name: str, messages: Dict) -> Generator:
    stream = ollama.chat(
        model=model_name, messages=messages, stream=True)
    for chunk in stream:
        yield chunk['message']['content']

username = os.getenv("USERNAME")

url_1 = "https://perpendicular.web.za/sitepad-data/uploads/2023/10/Perpendicular_Logo_edited-1.png"
response_1 = urllib.request.urlopen(url_1)

url_2 = "https://perpendicular.web.za/sitepad-data/uploads/2024/05/powered_by_ollama.png"
response_2 = urllib.request.urlopen(url_2)

image_1 = Image.open(response_1)
image_2 = Image.open(response_2)

st.sidebar.image(image_1, caption='Perp Logo', use_column_width=True)

# Display image as banner above the title
st.image(image_2, use_column_width=True)

# Center the title using CSS
st.markdown("<h1 style='text-align: center;'>Promptus Web App</h1>", unsafe_allow_html=True)

if "selected_model" not in st.session_state:
    st.session_state.selected_model = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

st.session_state.selected_model = st.sidebar.selectbox(
    "Please select the model:", [model["name"] for model in ollama.list()["models"]])

# Load chat history from JSON file if it exists
if os.path.exists("chat_history.json"):
    with open("chat_history.json", "r") as f:
        st.session_state.messages = json.load(f)

# Display chat history in the sidebar
for message in st.session_state.messages:
    if message["role"] == "user":
        st.sidebar.markdown(f"**User:** {message['content']}")
    elif message["role"] == "assistant":
        st.sidebar.markdown(f"**Assistant:** {message['content']}")

if prompt := st.chat_input("How could I help you?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = st.write_stream(ollama_generator(
            st.session_state.selected_model, st.session_state.messages))
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
    # Store messages to JSON file
    with open("chat_history.json", "w") as f:
        json.dump(st.session_state.messages, f)
    # Update sidebar with latest user/assistant pair
    if st.session_state.messages[-2]["role"] == "user":
        st.sidebar.markdown(f"**User:** {st.session_state.messages[-2]['content']}")
    if st.session_state.messages[-1]["role"] == "assistant":
        st.sidebar.markdown(f"**Assistant:** {st.session_state.messages[-1]['content']}")