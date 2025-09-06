FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN apt-get update && apt-get install -y build-essential libpq-dev     && pip install --no-cache-dir -r requirements.txt     && apt-get remove -y build-essential libpq-dev && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]
