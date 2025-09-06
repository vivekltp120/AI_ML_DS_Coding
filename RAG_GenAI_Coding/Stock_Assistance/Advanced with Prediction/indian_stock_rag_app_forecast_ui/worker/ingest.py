import os
import yfinance as yf
import datetime
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from prophet import Prophet
import pandas as pd

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "stocks"

tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

def fetch_daily_prices(ticker):
    today = datetime.date.today()
    data = yf.download(ticker, start=today - datetime.timedelta(days=60), end=today)
    rows = []
    for date, row in data.iterrows():
        text = (
            f"On {date.date()}, {ticker} closed at ₹{row['Close']:.2f} "
            f"(Open: ₹{row['Open']:.2f}, High: ₹{row['High']:.2f}, "
            f"Low: ₹{row['Low']:.2f}, Volume: {row['Volume']:.0f})."
        )
        rows.append((date.date().isoformat(), text))
    return rows

def forecast_prices(ticker, periods=7):
    df = yf.download(ticker, period="1y", interval="1d").reset_index()
    df = df.rename(columns={"Date": "ds", "Close": "y"})
    model_f = Prophet()
    model_f.fit(df[["ds", "y"]])
    future = model_f.make_future_dataframe(periods=periods)
    forecast = model_f.predict(future)
    results = []
    for _, row in forecast.tail(periods).iterrows():
        text = (
            f"Forecast: On {row['ds'].date()}, {ticker} is projected to close around "
            f"₹{row['yhat']:.2f} (range ₹{row['yhat_lower']:.2f} – ₹{row['yhat_upper']:.2f})."
        )
        results.append((row["ds"].date().isoformat(), text))
    return results

def ingest():
    for ticker in tickers:
        # Ingest daily prices
        prices = fetch_daily_prices(ticker)
        for date, text in prices:
            embedding = model.encode(text).tolist()
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=[{
                    "id": f"{ticker}_price_{date}",
                    "vector": embedding,
                    "payload": {
                        "ticker": ticker,
                        "date": date,
                        "type": "price",
                        "text": text
                    }
                }]
            )
        # Ingest forecast (default 7 days)
        forecasts = forecast_prices(ticker, periods=7)
        for date, text in forecasts:
            embedding = model.encode(text).tolist()
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=[{
                    "id": f"{ticker}_forecast_{date}",
                    "vector": embedding,
                    "payload": {
                        "ticker": ticker,
                        "date": date,
                        "type": "forecast",
                        "text": text
                    }
                }]
            )
        print(f"Ingested {ticker} prices and forecasts.")

if __name__ == "__main__":
    ingest()
