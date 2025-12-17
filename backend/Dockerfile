FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including audio libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libsndfile1 \
    libsndfile1-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application (PORT env var is set by Cloud Run)
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
