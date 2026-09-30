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

# Explicitly start the application
CMD ["sh","-c","uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
