import streamlit as st
import requests
import NoogleDriver
from noogleai import NoogleAI

NoogleDriver.driverReady.wait()
noogleDriver = NoogleDriver.noogleDriver
print(noogleDriver)

def summarizer(ask):
    client = NoogleAI(text_instruction=ask)
    summarized = client.summarizeResults(driver=noogleDriver)
    return summarized

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Function to handle user input
def handle_input():
    user_message = st.session_state.user_input
    if user_message:
        st.session_state.chat_history.append(('user', user_message))
        bot_response = summarizer(user_message)
        st.session_state.chat_history.append(('bot', bot_response))
        st.session_state.user_input = ""

# Streamlit app layout
st.title("Chat Interface")

# Display chat history
st.subheader("Chat History")
for sender, message in st.session_state.chat_history:
    if sender == 'user':
        st.markdown(
            f'<p style="color: blue; background-color: #f0f0f0; padding: 10px; border-radius: 10px;">You: {message}</p>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<p>{message[0]}</p><p>Sources: <br>{"<br>".join(message[1])}</p>',
            unsafe_allow_html=True
        )

# User input
st.text_input("Type your message:", key="user_input", on_change=handle_input)

# Clear history button
if st.button("Clear History"):
    st.session_state.chat_history = []
