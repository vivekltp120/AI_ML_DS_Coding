from langchain_core.prompts import ChatPromptTemplate
from langserve import add_routes
from fastapi import FastAPI
from langchain_community.llms import ollama
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()
## Langsmith tracking
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")

## Prompt Template
#creating app interface with langserve and langchain
app=FastAPI(
    title="Langserve App",
    description="A simple Langserve app with Langchain",
    version="0.1.0",
)

# Add routes to the FastAPI app

prompt=ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that translates {input_language} to {output_language}"),
        ("human", "{text}"),
    ]
)

llm=ollama.Ollama(model="llama3")

add_routes(
    app,
    prompt | llm,
    path="/ollama"
    )

if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    uvicorn.run(app, host="127.0.0.1",port=8080)












