import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
QHOST = os.getenv("QDRANT_HOST", "localhost")
QPORT = int(os.getenv("QDRANT_PORT", 6333))
COLL = os.getenv("COLLECTION_NAME", "market_docs")

_embedder = None
_client = None

def embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder

def client():
    global _client
    if _client is None:
        _client = QdrantClient(host=QHOST, port=QPORT)
    return _client
