from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
from .settings import settings
from .rag import retrieve, build_prompt, generate

app = FastAPI(title="Indian Stock RAG API")

@app.on_event("startup")
async def startup():
    client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
    embedder = SentenceTransformer(settings.embedding_model)
    dim = embedder.get_sentence_embedding_dimension()
    collections = [c.name for c in client.get_collections().collections]
    if settings.collection not in collections:
        client.recreate_collection(
            collection_name=settings.collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

class QueryIn(BaseModel):
    question: str
    tickers: Optional[List[str]] = None
    top_k: int = 6

@app.post("/query")
async def query(payload: QueryIn):
    hits = await retrieve(payload.question, payload.tickers, payload.top_k)
    prompt = build_prompt(payload.question, hits)
    answer = await generate(prompt)
    return {
        "answer": answer,
        "matches": [
            {
                "id": h.id,
                "score": h.score,
                "ticker": h.payload.get("ticker"),
                "date": h.payload.get("date"),
                "dtype": h.payload.get("dtype"),
                "text": h.payload.get("text"),
            } for h in hits
        ]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
