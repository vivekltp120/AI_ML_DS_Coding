import os
import httpx
import pandas as pd
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="India Stock RAG", layout="wide")

st.title("🇮🇳 Indian Stock Market Assistant (RAG)")

with st.sidebar:
    st.header("Query")
    question = st.text_area("Ask a question", "What is the latest technical overview for RELIANCE.NS?")
    tickers = st.text_input("Restrict to tickers (comma-separated)", "RELIANCE.NS,TCS.NS").strip()
    top_k = st.slider("Top-K context", 2, 12, 6)
    go = st.button("Ask")

if go:
    payload = {
        "question": question,
        "tickers": [t.strip() for t in tickers.split(',') if t.strip()],
        "top_k": top_k,
    }
    with st.spinner("Retrieving & generating..."):
        try:
            r = httpx.post(f"{API_BASE}/query", json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()
    st.subheader("Answer")
    st.write(data.get("answer", ""))

    st.subheader("Context Used")
    matches = data.get("matches", [])
    if matches:
        df = pd.DataFrame(matches)
        st.dataframe(df[["ticker","date","score","dtype","text"]])
    else:
        st.info("No matches found.")

st.caption("Not investment advice. For educational use only.")
