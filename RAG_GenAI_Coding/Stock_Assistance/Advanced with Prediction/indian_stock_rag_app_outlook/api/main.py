from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import pandas as pd
from qdrant_client.models import FieldCondition, MatchValue, Filter

load_dotenv()

app = FastAPI(title="Indian Stock RAG API")

QDRANT_HOST = os.getenv('QDRANT_HOST', 'qdrant')
QDRANT_PORT = int(os.getenv('QDRANT_PORT', 6333))
COLLECTION = os.getenv('COLLECTION_NAME', 'market_docs')

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
embedder = SentenceTransformer(os.getenv('EMBEDDING_MODEL', 'BAAI/bge-small-en-v1.5'))

class QueryIn(BaseModel):
    question: str
    tickers: Optional[List[str]] = None
    top_k: int = 6

@app.post('/query')
def query(payload: QueryIn):
    vec = embedder.encode(payload.question).tolist()
    flt = None
    if payload.tickers:
        must = [FieldCondition(key='ticker', match=MatchValue(value=payload.tickers))]
        flt = Filter(must=must)
    hits = client.search(collection_name=COLLECTION, query_vector=vec, limit=payload.top_k, query_filter=flt)
    texts = [h.payload.get('text') for h in hits if h.payload]
    answer = "\n\n".join(texts) if texts else "No context found."
    return {'answer': answer, 'matches': [{'id': h.id, 'score': h.score, 'payload': h.payload} for h in hits]}

@app.get('/forecast/{ticker}')
def forecast(ticker: str, days: int = 7):
    must = [FieldCondition(key='ticker', match=MatchValue(value=[ticker])), FieldCondition(key='dtype', match=MatchValue(value=['forecast']))]
    flt = Filter(must=must)
    # Qdrant requires a vector for search; use zero vector as placeholder
    dim = embedder.get_sentence_embedding_dimension()
    zero_vec = [0.0]*dim
    hits = client.search(collection_name=COLLECTION, query_vector=zero_vec, limit=100, query_filter=flt)
    forecasts = []
    for h in hits:
        p = h.payload or {}
        if p.get('ticker') == ticker and p.get('dtype') == 'forecast':
            forecasts.append(p)
    if not forecasts:
        raise HTTPException(status_code=404, detail='No forecasts found for ticker')
    return {'ticker': ticker, 'requested_days': days, 'forecasts': forecasts}

@app.get('/outlook/{ticker}')
def outlook(ticker: str, news_days: int = 3, forecast_days: int = 7):
    dim = embedder.get_sentence_embedding_dimension()
    zero_vec = [0.0]*dim
    # Latest signal
    must_sig = [FieldCondition(key='ticker', match=MatchValue(value=[ticker])), FieldCondition(key='dtype', match=MatchValue(value=['signal']))]
    sig_hits = client.search(collection_name=COLLECTION, query_vector=zero_vec, limit=10, query_filter=Filter(must=must_sig))
    signals = [h.payload for h in sig_hits if h.payload]
    latest_signal = None
    if signals:
        signals_sorted = sorted(signals, key=lambda p: p.get('date',''), reverse=True)
        latest_signal = signals_sorted[0]

    # News (last news_days)
    must_news = [FieldCondition(key='ticker', match=MatchValue(value=[ticker])), FieldCondition(key='dtype', match=MatchValue(value=['news']))]
    news_hits = client.search(collection_name=COLLECTION, query_vector=zero_vec, limit=200, query_filter=Filter(must=must_news))
    since = (pd.Timestamp.utcnow().normalize() - pd.Timedelta(days=news_days)).date().isoformat()
    news_items = [h.payload for h in news_hits if h.payload and h.payload.get('date','') >= since]
    avg_sent = None
    if news_items:
        vals = [float(n.get('sentiment',0.0)) for n in news_items if n.get('sentiment') is not None]
        if vals:
            avg_sent = sum(vals)/len(vals)

    # Forecasts
    must_fc = [FieldCondition(key='ticker', match=MatchValue(value=[ticker])), FieldCondition(key='dtype', match=MatchValue(value=['forecast']))]
    fc_hits = client.search(collection_name=COLLECTION, query_vector=zero_vec, limit=200, query_filter=Filter(must=must_fc))
    forecasts = [h.payload for h in fc_hits if h.payload]

    # Recent snapshots
    must_snap = [FieldCondition(key='ticker', match=MatchValue(value=[ticker])), FieldCondition(key='dtype', match=MatchValue(value=['daily_snapshot']))]
    snap_hits = client.search(collection_name=COLLECTION, query_vector=zero_vec, limit=20, query_filter=Filter(must=must_snap))
    snapshots = [h.payload for h in snap_hits if h.payload]

    if not (latest_signal or news_items or forecasts or snapshots):
        raise HTTPException(status_code=404, detail='No data available for ticker')

    return {
        "ticker": ticker,
        "latest_signal": latest_signal,
        "avg_news_sentiment": avg_sent,
        "news_count": len(news_items),
        "forecasts": forecasts,
        "snapshots": snapshots,
        "news_items": news_items
    }
