FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN apt update && apt install -y build-essential libatlas-base-dev     && pip install --no-cache-dir -r requirements.txt     && apt remove -y build-essential libatlas-base-dev && apt autoremove -y && rm -rf /var/lib/apt/lists/*
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["streamlit","run","app.py","--server.address","0.0.0.0","--server.port","8501"]
