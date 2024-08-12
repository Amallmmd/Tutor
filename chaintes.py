from langchain.chains import ConversationChain, SimpleSequentialChain, LLMChain
from langchain_openai import ChatOpenAI,OpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
# Initialize the language model
llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        openai_api_key=api_key)
# Create a memory component
memory = ConversationBufferMemory(input_key="input", memory_key="chat_history")

# Define ConversationChain
conversation_chain = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# Define steps for SimpleSequentialChain

# Step 1: Analyze sentiment
sentiment_template = "Analyze the sentiment of this text: {input}"
sentiment_prompt = PromptTemplate(input_variables=["input"], template=sentiment_template)
sentiment_chain = LLMChain(llm=llm, prompt=sentiment_prompt)

# Step 2: Extract key topics
topics_template = "Extract the main topics from this text: {input}"
topics_prompt = PromptTemplate(input_variables=["input"], template=topics_template)
topics_chain = LLMChain(llm=llm, prompt=topics_prompt)

# Step 3: Generate follow-up questions
questions_template = """
Based on the following:
Sentiment: {sentiment}
Topics: {topics}
Original text: {original_input}

Generate three follow-up questions to continue the conversation.
"""
questions_prompt = PromptTemplate(input_variables=["sentiment", "topics", "original_input"], template=questions_template)
questions_chain = LLMChain(llm=llm, prompt=questions_prompt)

# Combine into SimpleSequentialChain
analysis_chain = SimpleSequentialChain(
    chains=[sentiment_chain, topics_chain, questions_chain],
    verbose=True
)

# Main chatbot loop
while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        break
    
    # Process through ConversationChain
    conversation_response = conversation_chain.predict(input=user_input)
    print("AI:", conversation_response)
    
    # Process through SimpleSequentialChain for analysis
    analysis_result = analysis_chain.run(user_input)
    
    # Extract follow-up questions from analysis result
    follow_up_questions = analysis_result.split('\n')[-3:]  # Assuming last 3 lines are questions
    
    print("\nFollow-up questions:")
    for question in follow_up_questions:
        print(question)
    
    print("\n")  # Add a newline for readability