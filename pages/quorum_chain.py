import mysql.connector
import streamlit as st
from langchain.chains import SequentialChain,SimpleSequentialChain, LLMChain
from langchain_openai import ChatOpenAI,OpenAI
from langchain.prompts import PromptTemplate
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
def create_chain(prompt_template,input_key,output_key):
    llm = ChatOpenAI(
        model_name="gpt-4-turbo",
        openai_api_key=api_key)
    prompt=PromptTemplate(template=prompt_template,input_variables=[input_key])
    return LLMChain(llm=llm, prompt=prompt, output_key=output_key)

#Main chat response function
def process_input(user_input):
    prompts = fetch_prompts()
    if not prompts:
        st.error("No prompts found in the database.")
    algebra_prompt = prompts[2][1]
    alg_pro = "You are an expert in algebra. Solve the following problem: {question}"
    tutor_prompt = prompts[2][2] 
    tut_pro = "You are a helpful tutor. Explain the following concept: {algebra_answer}"
    personality_prompt = prompts[2][3]
    # personality_prompt = "You are a friendly AI assistant. Respond to the following in a more Natural manner: {tutor_explanation}"
    print(algebra_prompt)
    print(tutor_prompt)
    # print(pers_pro)
    algebra_chain = create_chain(algebra_prompt, "question", "algebra_answer")
    tutor_chain = create_chain(tutor_prompt, "algebra_answer", "tutor_explanation")
    personality_chain = create_chain(personality_prompt, "tutor_explanation", "final_answer")
    
    #Create sequential chain
    overall_chain = SequentialChain(
        chains=[algebra_chain, tutor_chain, personality_chain],
        input_variables=["question"],
        output_variables=["final_answer"],
        verbose=True
    )
    # result = overall_chain({"question": user_input, **st.session_state.memory.load()})
    
    # # Update memory with the latest interaction
    # st.session_state.memory.save_context({"question": user_input}, {"final_answer": result["final_answer"]})
    
    # return result["final_answer"]
    return overall_chain.run(user_input)

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'memory' not in st.session_state:
    st.session_state.memory = SimpleMemory()

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
            response = process_input(input_prompt)
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # try:
        #     algebra_response = algebra_chain.run({"user_input": user_input})
        #     tutor_response = tutor_chain.run({"user_input": algebra_response})
        #     personality_response = personality_chain.run({"user_input": tutor_response})
            
        #     # Add responses to chat history
        #     st.session_state.messages.append(("Algebra Prompt", algebra_response))
        #     st.session_state.messages.append(("Tutor Prompt", tutor_response))
        #     st.session_state.messages.append(("Personality Prompt", personality_response))
        # except Exception as e:
        #     st.error(f"An error occurred: {e}")
if __name__ == "__main__":
    run_app()