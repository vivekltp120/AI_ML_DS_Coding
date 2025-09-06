# Indian Stock Market RAG (Docker + FastAPI + Streamlit + Qdrant + Ollama)

An end-to-end Retrieval-Augmented Generation (RAG) app for Indian equities and technical indicators.
Stack: FastAPI backend, Streamlit UI, Qdrant vector DB, Ollama-hosted open-source LLM, and a worker that updates the vector DB daily.

Quick Start
1. Copy .env.example to .env and edit if needed:
   cp .env.example .env

2. Launch:
   docker compose up -d --build

3. UI: http://localhost:8501
   API docs: http://localhost:8000/docs

Notes
- NSE tickers end with .NS
- Embeddings: BAAI/bge-small-en-v1.5 (CPU-friendly)
- LLM via Ollama: qwen2.5:7b-instruct (default)
- Vector DB: Qdrant
- Daily updates scheduled at CRON_DAILY (default 18:00 IST)
