import mysql.connector
import streamlit as st
from langchain.chains import ConversationChain,SimpleSequentialChain, LLMChain
from langchain_openai import ChatOpenAI,OpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.memory import SimpleMemory
from distutils import debug
from typing import Literal
from dataclasses import dataclass
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# @dataclass
# class Message:
#     origin: Literal["human", "ai"]
#     message: str

# client = OpenAI()
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="****",
    database="newdb"
)
mycursor=mydb.cursor()

def fetch_prompts():
    mycursor.execute("SELECT id, algebra_prompt, tutor_prompt, personality_prompt FROM prompt")
    return mycursor.fetchall()

def get_openai_response(prompt, user_input):
    pass
    # return llm.choices[0].text.strip()
def create_chain(prompt_template):
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        openai_api_key=api_key)
    prompt=PromptTemplate(template=prompt_template,input_variables=["question"])
    return LLMChain(llm=llm, prompt=prompt)

if 'messages' not in st.session_state:
    st.session_state.messages = []
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True)

conversation_chain = ConversationChain(
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        openai_api_key=api_key),
    memory=st.session_state.memory,
    verbose=True
)
def process_input(user_input):
    prompts = fetch_prompts()
    if not prompts:
        st.error("No prompts found in the database.")
    algebra_prompt = prompts[4][1]
    alg_pro = "You are an expert in algebra. Solve the following problem: {question}"
    tutor_prompt = prompts[4][2] 
    tut_pro = "You are a helpful tutor. Explain the following concept: {algebra_answer}"
    personality_prompt = prompts[3][3]
    # print(algebra_prompt)
    # print(tutor_prompt)

    algebra_chain = create_chain(algebra_prompt)
    tutor_chain = create_chain(tutor_prompt)
    personality_chain = create_chain(personality_prompt)

    overall_chain = SimpleSequentialChain(
        chains=[algebra_chain, tutor_chain, personality_chain],
        verbose=True,
    )
    
    # Process the input through the chain
    return overall_chain.run(user_input)

def run_app():
    st.title("Quorum QA")    
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if input_prompt := st.chat_input("What's your question?"):
        # Add user message to chat history
        with st.chat_message("user"):
            st.markdown(input_prompt)
        st.session_state.messages.append({"role": "User", "content":input_prompt})
        # Generate responses
        with st.chat_message("assistant"):
            with st.spinner("Thinking.."):
                response = conversation_chain.predict(input=input_prompt)
                conversation_response = process_input(response)
                st.markdown(conversation_response)
                st.session_state.messages.append({"role": "assistant", "content": conversation_response})
        
    #     with st.spinner("Analyzing..."):
    #         analysis_result = process_input(input_prompt)
    #         follow_up_questions = analysis_result.split('\n')[-3:]  # Assuming last 3 lines are questions

    # # Display follow-up questions
    #     with st.expander("Suggested follow-up questions"):
    #         for question in follow_up_questions:
    #             st.markdown(f"- {question}")
        

if __name__ == "__main__":
    run_app()