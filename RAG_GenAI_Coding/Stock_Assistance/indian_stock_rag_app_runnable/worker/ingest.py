import os
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client import QdrantClient
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from utils import embedder, client, COLL

from indicators import compute_indicators, row_to_summary

load_dotenv()

TICKERS = [t.strip() for t in os.getenv("TICKERS", "RELIANCE.NS,TCS.NS").split(",") if t.strip()]
HISTORY_DAYS = int(os.getenv("HISTORY_DAYS", 365))
CRON_DAILY = os.getenv("CRON_DAILY", "0 18 * * *")  # 6pm IST

qclient: QdrantClient = client()
embed = embedder()

# Ensure collection exists
DIM = embed.get_sentence_embedding_dimension()
collections = [c.name for c in qclient.get_collections().collections]
if COLL not in collections:
    qclient.recreate_collection(COLL, vectors_config=VectorParams(size=DIM, distance=Distance.COSINE))

def ingest_once():
    print(f"[INGEST] Starting at {datetime.now().isoformat()} | Universe={len(TICKERS)}")
    start = datetime.utcnow() - timedelta(days=HISTORY_DAYS)
    total_points = 0
    for ticker in TICKERS:
        try:
            df = yf.download(ticker, start=start.date(), progress=False, auto_adjust=False)
            if df.empty:
                print(f"[WARN] No data for {ticker}")
                continue
            df = df.reset_index().rename(columns={"Date": "date"})
            df = compute_indicators(df)
            payloads = []
            vectors = []
            ids = []
            for _, row in df.iterrows():
                text = row_to_summary(ticker, row)
                payloads.append({
                    "ticker": ticker,
                    "date": str(row["date"].date()),
                    "dtype": "daily_snapshot" ,
                    "text": text,
                })
                vectors.append(embed.encode(text).tolist())
                # deterministic id
                ids.append(int(pd.Timestamp(row["date"]).strftime("%Y%m%d")))
            if payloads:
                qclient.upsert(collection_name=COLL, points=[
                    PointStruct(id=f"{ticker}-{pid}", vector=v, payload=p)
                    for pid, v, p in zip(ids, vectors, payloads)
                ])
                total_points += len(payloads)
                print(f"[OK] {ticker}: upserted {len(payloads)} points")
        except Exception as e:
            print(f"[ERR] {ticker}: {e}")
            continue
    print(f"[DONE] Total points upserted: {total_points}")

def schedule():
    scheduler = BlockingScheduler(timezone="Asia/Kolkata")
    minute, hour, *_ = CRON_DAILY.split()
    scheduler.add_job(ingest_once, 'cron', minute=minute, hour=hour, id='daily_ingest', replace_existing=True)
    print(f"[SCHED] Daily job scheduled at {hour}:{minute} IST")
    ingest_once()  # initial run on boot
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    schedule()
