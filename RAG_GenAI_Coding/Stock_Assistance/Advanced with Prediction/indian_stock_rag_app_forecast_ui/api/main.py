from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import os
import yfinance as yf
from prophet import Prophet

app = FastAPI()

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "stocks"

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def query_rag(req: QueryRequest):
    query_vector = model.encode(req.query).tolist()
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=3
    )
    context = [r.payload for r in results]
    answer = "Based on stock data: " + " ".join([c["text"] for c in context])
    return {"answer": answer, "context": results}

@app.get("/forecast/{ticker}")
def forecast(ticker: str, days: int = 7):
    df = yf.download(ticker, period="1y", interval="1d").reset_index()
    df = df.rename(columns={"Date": "ds", "Close": "y"})
    model_f = Prophet()
    model_f.fit(df[["ds", "y"]])
    future = model_f.make_future_dataframe(periods=days)
    forecast = model_f.predict(future)
    data = forecast.tail(days).to_dict(orient="records")
    return {"ticker": ticker, "forecast": data}
