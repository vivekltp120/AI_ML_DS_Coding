from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]=os.getenv("LANGCHAIN_PROJECT","Ollama Langchain Experiment")
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")

## Prompt Template

assist_prompt=ChatPromptTemplate.from_messages(
    [
        ("system","You are a helpful assistant. Please response to the user queries"),
        ("user","Question:{question}")
    ]
)

translator_prompt=ChatPromptTemplate.from_messages(
    [
        ("system", "translates {input_language} to {output_language}"),
        ("human", "{question}"),
    ]
)

## streamlit framework

st.title(f'Langchain Demo With OLLama API')
model=st.selectbox(
    "Select the LLM Model",
    options=["gemma3", "phi4"],
    index=0,
    help="Select the model you want to use for the translation",
)
context=st.selectbox(
    "Select the Context for Model",
    options=["Translation", "Assistance"],
    index=1,
    help="Select the Context"
)

if context == "Translation":
    prompt = translator_prompt
    from_language=st.selectbox("Input Language", ["English", "Hindi", "French"])
    to_language=st.selectbox("Output Language", ["English", "Hindi", "French"])
else:
    prompt = assist_prompt
     
# input_text=st.text_input("Model Input", placeholder="Enter your text here...")
input_text=st.chat_input("Chat Input")
# ollama LLAma2 LLm 
from langchain_ollama import OllamaLLM
llm = OllamaLLM(model=model)
output_parser=StrOutputParser()
chain=prompt|llm|output_parser

if input_text:
    if context == "Translation":
        contex_query={"question":input_text,"input_language":from_language,"output_language":to_language}
    else:    
        contex_query={"question":input_text}
    st.write(chain.invoke(contex_query))