from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA, ConversationChain
from langchain_openai import ChatOpenAI
from prompts.prompts import Template
import base64
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Literal
from dataclasses import dataclass
import time
import random

load_dotenv()

# client = OpenAI()
api_key = os.getenv("OPENAI_API_KEY")
# api_key = st.secrets['OPENAI_API_KEY']

@dataclass
class Message:
    """Class for keeping track of interview history."""
    origin: Literal["human", "ai"]
    message: str

def text_to_speech(speech_file_path,input_chat):
    client = OpenAI(api_key=api_key)
    response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=input_chat
    )
    response.stream_to_file(speech_file_path)
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(Message(origin="ai", message="Hey kid I am here to guide you to the world of Algebra. Feel free to ask me your doubts and concerts, I'll be there with you"))

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(human_prefix = "Student", ai_prefix = "Tutor")
    
if "bot_response" not in st.session_state:
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        # model_name="gpt-4o",
        temperature=0.5,)
    st.session_state.bot_response = ConversationChain(
        prompt = PromptTemplate(input_variables = ["history", "input"], template = Template.algebra_template),
        llm = llm,
        memory= st.session_state.memory
    )

# GUI components
def main():
    st.title("Math Tutor")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message.origin):
            st.markdown(message.message)

    # Accept user input
    if user_input := st.chat_input("What is up?"):
        # Display user message in chat message container
        with st.chat_message("human"):
            st.markdown(user_input)
            # Add user message to chat history
            st.session_state.messages.append(Message(origin="human", message=user_input))
        # response of the bot through voice
        tutor_response = st.session_state.bot_response.run(user_input)
        with st.chat_message("assistant"):
            st.markdown(tutor_response)
            # Add assistant response to chat history
            st.session_state.messages.append(Message(origin="ai", message=tutor_response))
        audio_output = "chatbot/audiofileout.wav"
        text_to_speech(speech_file_path=audio_output,input_chat=tutor_response)
        autoplay_audio(audio_output)

if __name__ == "__main__":
    main()