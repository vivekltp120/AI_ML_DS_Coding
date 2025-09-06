import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_URL = "http://api:8000"

st.set_page_config(page_title="Indian Stock Market Assistant", layout="wide")

tab1, tab2 = st.tabs(["💬 Q&A", "🔮 Forecasting"])

with tab1:
    st.title("📈 Indian Stock Market RAG Assistant")
    query = st.text_input("Enter your question (e.g., 'What was TCS stock price yesterday?')")
    if st.button("Ask") and query:
        with st.spinner("Fetching answer..."):
            try:
                response = requests.post(f"{API_URL}/query", json={"query": query})
                if response.status_code == 200:
                    result = response.json()
                    st.subheader("Answer")
                    st.write(result.get("answer", "No answer"))
                    st.subheader("Context Used")
                    for doc in result.get("context", []):
                        st.write(f"- {doc['payload']['text']}")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")

with tab2:
    st.title("🔮 Stock Price Forecasting")
    ticker = st.selectbox("Select a stock", ["RELIANCE.NS", "TCS.NS", "INFY.NS"])
    days = st.slider("Forecast horizon (days)", min_value=3, max_value=30, value=7)
    if st.button("Get Forecast"):
        with st.spinner("Generating forecast..."):
            try:
                response = requests.get(f"{API_URL}/forecast/{ticker}?days={days}")
                if response.status_code == 200:
                    data = response.json()["forecast"]
                    df = pd.DataFrame(data)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df["ds"], y=df["yhat"], mode="lines", name="Forecast"))
                    fig.add_trace(go.Scatter(x=df["ds"], y=df["yhat_lower"], mode="lines", name="Lower Bound", line=dict(dash="dot")))
                    fig.add_trace(go.Scatter(x=df["ds"], y=df["yhat_upper"], mode="lines", name="Upper Bound", line=dict(dash="dot")))
                    st.plotly_chart(fig, use_container_width=True)
                    st.subheader("Forecast Data")
                    st.dataframe(df[["ds", "yhat", "yhat_lower", "yhat_upper"]])
                    st.warning("⚠️ Forecasts are statistical projections only. Not financial advice.")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")
