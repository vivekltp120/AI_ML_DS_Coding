import os
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

API_BASE = os.getenv('API_BASE', 'http://api:8000')
TICKERS = os.getenv('TICKERS', 'RELIANCE.NS,TCS.NS').split(',')

st.set_page_config(page_title='India Stock RAG + Outlook', layout='wide')
st.title('🇮🇳 Indian Stock Market Assistant — RAG + Outlook')

tabs = st.tabs(['Q&A', 'Forecasting', 'Outlook'])

with tabs[0]:
    st.header('Ask a question (RAG)')
    q = st.text_area('Question', value='What is the latest technical overview for RELIANCE.NS?')
    tickers = st.text_input('Restrict to tickers (comma-separated)', value=','.join(TICKERS))
    top_k = st.slider('Top-K context', 2, 12, 6)
    if st.button('Ask'):
        payload = {'question': q, 'tickers': [t.strip() for t in tickers.split(',') if t.strip()], 'top_k': top_k}
        with st.spinner('Retrieving...'):
            try:
                r = requests.post(f'{API_BASE}/query', json=payload, timeout=120)
                r.raise_for_status()
                data = r.json()
                st.subheader('Answer')
                st.write(data.get('answer', ''))
                st.subheader('Context Used')
                matches = data.get('matches', [])
                if matches:
                    df = pd.DataFrame([m['payload'] for m in matches])
                    st.dataframe(df[['ticker','date','dtype','text']])
                else:
                    st.info('No matches found.')
            except Exception as e:
                st.error(f'API error: {e}')

with tabs[1]:
    st.header('Forecasting Dashboard')
    options = [t.strip() for t in TICKERS if t.strip()]
    sel = st.selectbox('Select ticker', options)
    days = st.slider('Forecast horizon (days)', min_value=3, max_value=30, value=7, step=1)
    hist_days = st.slider('History window (days)', min_value=90, max_value=1095, value=365, step=30)
    if st.button('Generate Forecast'):
        with st.spinner('Fetching forecast and historical data...'):
            try:
                r = requests.get(f'{API_BASE}/forecast/{sel}?days={days}', timeout=120)
                r.raise_for_status()
                data = r.json()
                forecasts = data.get('forecasts', [])
                import yfinance as yf
                end = datetime.utcnow().date()
                start = end - timedelta(days=hist_days)
                df = yf.download(sel, start=start, end=end, progress=False, auto_adjust=False).reset_index()
                if df.empty:
                    st.error('No historical data found.')
                else:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close'))
                    if forecasts:
                        fc_df = pd.DataFrame(forecasts)
                        fc_df['date'] = pd.to_datetime(fc_df['date'])
                        fig.add_trace(go.Scatter(x=fc_df['date'], y=fc_df['yhat'], name='Forecast'))
                        fig.add_trace(go.Scatter(x=fc_df['date'], y=fc_df['yhat_upper'], name='Upper', line=dict(dash='dash')))
                        fig.add_trace(go.Scatter(x=fc_df['date'], y=fc_df['yhat_lower'], name='Lower', line=dict(dash='dash')))
                    fig.update_layout(title=f'{sel} — Price & Forecast', xaxis_title='Date', yaxis_title='Price (INR)')
                    st.plotly_chart(fig, use_container_width=True)
                    st.subheader('Forecast summary (text)')
                    for f in forecasts:
                        st.write(f.get('text'))
            except Exception as e:
                st.error(f'Error fetching forecast: {e}')

with tabs[2]:
    st.header('Combined Outlook')
    options = [t.strip() for t in TICKERS if t.strip()]
    sel = st.selectbox('Select ticker for Outlook', options, index=0)
    news_days = st.number_input('News lookback (days)', min_value=1, max_value=30, value=3)
    if st.button('Get Outlook'):
        with st.spinner('Fetching outlook...'):
            try:
                r = requests.get(f'{API_BASE}/outlook/{sel}?news_days={news_days}', timeout=120)
                r.raise_for_status()
                data = r.json()
                st.subheader('Latest Signal')
                st.write(data.get('latest_signal') or 'No signal available')
                st.subheader('News Sentiment (avg)')
                avg = data.get('avg_news_sentiment')
                st.metric('Average sentiment (compound)', f'{avg:.3f}' if avg is not None else 'N/A')
                st.subheader('Top News (most recent)')
                for n in data.get('news_items', [])[:10]:
                    st.write(f"- {n.get('title')} (sentiment={n.get('sentiment')})")
                st.subheader('Forecast Summary')
                for f in data.get('forecasts', []):
                    st.write(f.get('text'))
                st.subheader('Recent Snapshots')
                for s in data.get('snapshots', [])[:10]:
                    st.write(f"- {s.get('date')}: {s.get('text')}")
            except Exception as e:
                st.error(f'Outlook error: {e}')

st.caption('Forecasts and signals are statistical projections and not financial advice.')
