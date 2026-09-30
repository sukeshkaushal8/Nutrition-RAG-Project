FROM python:3.12-slim

WORKDIR /app

# Install build dependencies for some python packages if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Explicitly start the application
CMD ["python", "src/api/main.py"]
