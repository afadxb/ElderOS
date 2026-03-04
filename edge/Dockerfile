FROM python:3.11-slim

# Install OpenCV system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and config
COPY src/ ./src/
COPY config/ ./config/

# Create directories for runtime data
RUN mkdir -p /data/clips /app/models

ENTRYPOINT ["python", "-m", "src.main"]
