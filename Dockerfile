FROM python:3.12-slim

WORKDIR /app

# Ensure Python can import the local `src` package
ENV PYTHONPATH=/app

# Install build dependencies for some python packages if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Auto-ingest on first start if Chroma DB is empty, then start the API
EXPOSE 8000
CMD ["/bin/sh","-c", "\
  CHROMA_COUNT=$(python -c \"from src.retrieval.vector_store import VectorStore; vs=VectorStore(); print(vs.count())\" 2>/dev/null || echo 0); \
  echo \"Chroma vector count: $CHROMA_COUNT\"; \
  if [ \"$CHROMA_COUNT\" = \"0\" ]; then \
    echo \"Vector store empty - running full ingestion pipeline...\"; \
    python scripts/ingest.py --step all; \
    echo \"Ingestion complete.\"; \
  else \
    echo \"Vector store already populated ($CHROMA_COUNT vectors) - skipping ingestion.\"; \
  fi && \
  exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000 \
"]
