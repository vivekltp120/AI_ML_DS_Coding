from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue
from sentence_transformers import SentenceTransformer
import httpx
from .settings import settings

_embedder = SentenceTransformer(settings.embedding_model)
_client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

async def generate(prompt: str) -> str:
    url = f"http://{settings.ollama_host}:{settings.ollama_port}/api/generate"
    json = {"model": settings.ollama_model, "prompt": prompt, "stream": False}
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(url, json=json)
        r.raise_for_status()
        # Ollama returns JSON with 'response' or 'outputs' depending on version; handle common cases.
        data = r.json()
        if "response" in data:
            return data.get("response", "")
        if "outputs" in data and isinstance(data["outputs"], list) and data["outputs"]:
            return data["outputs"][0].get("content", "")
        return ""

async def retrieve(query: str, tickers: Optional[List[str]] = None, top_k: int = 6):
    vec = _embedder.encode(query).tolist()
    must = []
    if tickers:
        must.append(FieldCondition(key="ticker", match=MatchValue(value=tickers)))
    flt = Filter(must=must) if must else None
    hits = _client.search(collection_name=settings.collection, query_vector=vec, limit=top_k, query_filter=flt)
    return hits

def build_prompt(question: str, hits) -> str:
    ctx = []
    for h in hits:
        p = h.payload
        ctx.append(f"[Ticker: {p.get('ticker')} | Date: {p.get('date')} | Type: {p.get('dtype')}]\n{p.get('text')}")
    context = "\n\n".join(ctx)
    system = (
        "You are an Indian stock market assistant. Use ONLY the provided context. "
        "Answer concisely, include dates, and note limitations. If unsure, say so.\n"
    )
    return f"{system}\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
