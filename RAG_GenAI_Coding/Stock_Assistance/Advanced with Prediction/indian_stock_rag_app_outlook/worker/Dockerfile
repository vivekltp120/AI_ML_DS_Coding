FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN apt update && apt install -y build-essential gfortran libatlas-base-dev     && pip install --no-cache-dir -r requirements.txt     && apt remove -y build-essential gfortran libatlas-base-dev && apt autoremove -y && rm -rf /var/lib/apt/lists/*
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["python","ingest.py"]
