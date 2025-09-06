# Indian Stock Market RAG + Outlook (Signals, News Sentiment, Prophet Forecasts)

This project ingests daily OHLCV + indicators, computes rule-based signals, pulls optional news and sentiment, trains Prophet forecasts, stores all artifacts in Qdrant, and exposes a FastAPI + Streamlit UI with an Outlook dashboard.

Quick start:
1. Copy .env.example to .env and edit if needed:
   cp .env.example .env
   (optionally add NEWSAPI_KEY for news ingestion)

2. Launch:
   docker compose up -d --build

3. UI: http://localhost:8501
   API docs: http://localhost:8000/docs

Notes:
- Prophet may require build tools; the worker Dockerfile installs minimal tools to build dependencies.
- This is educational. Forecasts and signals are NOT financial advice.
