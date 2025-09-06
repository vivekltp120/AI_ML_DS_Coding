import os
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client import QdrantClient
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from prophet import Prophet
from indicators import compute_indicators, row_to_summary, compute_signal_for_row

import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

load_dotenv()

QHOST = os.getenv('QDRANT_HOST', 'qdrant')
QPORT = int(os.getenv('QDRANT_PORT', 6333))
COLL = os.getenv('COLLECTION_NAME', 'market_docs')
EMBED_MODEL = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-small-en-v1.5')

NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', None)
NEWS_FROM_DAYS = int(os.getenv('NEWS_FROM_DAYS', 3))

TICKERS = [t.strip() for t in os.getenv('TICKERS', 'RELIANCE.NS,TCS.NS').split(',') if t.strip()]
HISTORY_DAYS = int(os.getenv('HISTORY_DAYS', 365))
DEFAULT_FORECAST_DAYS = int(os.getenv('DEFAULT_FORECAST_DAYS', 7))

qclient = QdrantClient(host=QHOST, port=QPORT)
embed = SentenceTransformer(EMBED_MODEL)
sentiment_analyzer = SentimentIntensityAnalyzer()

DIM = embed.get_sentence_embedding_dimension()
collections = [c.name for c in qclient.get_collections().collections]
if COLL not in collections:
    qclient.recreate_collection(COLL, vectors_config=VectorParams(size=DIM, distance=Distance.COSINE))

def row_to_summary(ticker: str, row) -> str:
    fields = [
        f"Close={row.Close:.2f}",
        f"RSI14={row.rsi14:.2f}" if pd.notna(row.rsi14) else "RSI14=NA",
    ]
    if 'MACD_12_26_9' in row.index:
        fields.append(f"MACD={row.MACD_12_26_9:.2f}")
    else:
        fields.append("MACD=NA")
    if 'MACDs_12_26_9' in row.index:
        fields.append(f"Signal={row.MACDs_12_26_9:.2f}")
    else:
        fields.append("Signal=NA")
    if 'BBANDS_U_20_2.0' in row.index:
        fields.append(f"UpperBB={row.BBANDS_U_20_2.0:.2f}")
    else:
        fields.append("UpperBB=NA")
    if 'BBANDS_L_20_2.0' in row.index:
        fields.append(f"LowerBB={row.BBANDS_L_20_2.0:.2f}")
    else:
        fields.append("LowerBB=NA")
    fields.append(f"SMA20={row.sma20:.2f}" if pd.notna(row.sma20) else "SMA20=NA")
    fields.append(f"SMA50={row.sma50:.2f}" if pd.notna(row.sma50) else "SMA50=NA")
    return (f"Daily technical snapshot for {ticker}: " + ", ".join(fields) + ". Interpret cautiously; not investment advice.")

def fetch_news_for_ticker(ticker, from_days=3):
    if not NEWSAPI_KEY:
        return []
    q = ticker.split('.')[0]
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": q,
        "from": (datetime.utcnow() - timedelta(days=from_days)).date().isoformat(),
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 20,
        "apiKey": NEWSAPI_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        items = r.json().get("articles", [])
        return items
    except Exception:
        return []

def ingest_once():
    print(f"[INGEST] Starting ingest at {datetime.utcnow().isoformat()} for {len(TICKERS)} tickers")
    start = datetime.utcnow() - timedelta(days=HISTORY_DAYS)
    total = 0
    for ticker in TICKERS:
        try:
            df = yf.download(ticker, start=start.date(), progress=False, auto_adjust=False)
            if df.empty:
                print(f"[WARN] No data for {ticker}")
                continue
            df = df.reset_index().rename(columns={"Date": "date"})
            df = compute_indicators(df)

            points = []
            for _, row in df.iterrows():
                text = row_to_summary(ticker, row)
                payload = {"ticker": ticker, "date": str(row['date'].date()), "dtype": "daily_snapshot", "text": text}
                vec = embed.encode(text).tolist()
                pid = f"{ticker}-{row['date'].strftime('%Y%m%d')}"
                points.append(PointStruct(id=pid, payload=payload, vector=vec))

                sig = compute_signal_for_row(row)
                sig_payload = {"ticker": ticker, "date": str(row['date'].date()), "dtype": "signal", "signal": sig['signal'], "summary": sig['summary'], "text": sig['summary']}
                sig_vec = embed.encode(sig['summary']).tolist()
                sig_id = f"{ticker}-signal-{row['date'].strftime('%Y%m%d')}"
                points.append(PointStruct(id=sig_id, payload=sig_payload, vector=sig_vec))

            if points:
                qclient.upsert(collection_name=COLL, points=points)
                total += len(points)
                print(f"[OK] {ticker}: upserted {len(points)} snapshot+signal points")

            try:
                hist = df[['date', 'Close']].rename(columns={'date': 'ds', 'Close': 'y'})
                model = Prophet()
                model.fit(hist)
                future = model.make_future_dataframe(periods=DEFAULT_FORECAST_DAYS)
                fc = model.predict(future)
                fc_points = []
                for _, r in fc.tail(DEFAULT_FORECAST_DAYS).iterrows():
                    date_iso = r['ds'].date().isoformat()
                    text = (f"Forecast: On {date_iso}, {ticker} projected close ~ ₹{r['yhat']:.2f} "
                            f"(range ₹{r['yhat_lower']:.2f} - ₹{r['yhat_upper']:.2f}).")
                    payload = {"ticker": ticker, "date": date_iso, "dtype": "forecast", "text": text,
                               'yhat': float(r['yhat']), 'yhat_lower': float(r['yhat_lower']), 'yhat_upper': float(r['yhat_upper']), 'horizon': DEFAULT_FORECAST_DAYS}
                    vec = embed.encode(text).tolist()
                    pid = f"{ticker}-forecast-{date_iso}"
                    fc_points.append(PointStruct(id=pid, payload=payload, vector=vec))
                if fc_points:
                    qclient.upsert(collection_name=COLL, points=fc_points)
                    print(f"[OK] {ticker}: upserted {len(fc_points)} forecast points")
            except Exception as e:
                print(f"[WARN] Forecast failed for {ticker}: {e}")

            try:
                articles = fetch_news_for_ticker(ticker, from_days=NEWS_FROM_DAYS)
                news_points = []
                for art in articles:
                    title = art.get('title') or ""
                    desc = art.get('description') or ""
                    text = (title + ". " + desc).strip()
                    if not text:
                        continue
                    vs = sentiment_analyzer.polarity_scores(text)
                    compound = float(vs.get('compound', 0.0))
                    payload = {"ticker": ticker, "date": art.get('publishedAt', '')[:10], "dtype": "news",
                               "title": title, "url": art.get('url'), "text": text, "sentiment": compound}
                    vec = embed.encode(text).tolist()
                    nid = f"{ticker}-news-{art.get('publishedAt','')}-{abs(hash(title)) % (10**9)}"
                    news_points.append(PointStruct(id=nid, payload=payload, vector=vec))
                if news_points:
                    qclient.upsert(collection_name=COLL, points=news_points)
                    print(f"[OK] {ticker}: upserted {len(news_points)} news points")
            except Exception as e:
                print(f"[WARN] News ingestion failed for {ticker}: {e}")

        except Exception as e:
            print(f"[ERR] {ticker}: {e}")
    print(f"[DONE] Total points upserted: {total}")

def schedule():
    sched = BlockingScheduler(timezone='Asia/Kolkata')
    minute, hour, *_ = os.getenv('CRON_DAILY', '0 18 * * *').split()
    sched.add_job(ingest_once, 'cron', minute=minute, hour=hour, id='daily', replace_existing=True)
    ingest_once()
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == '__main__':
    schedule()
