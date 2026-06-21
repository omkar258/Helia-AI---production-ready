FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/tmp/hf_cache

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security (Hugging Face Spaces runs as user 1000)
RUN useradd -m -u 1000 user
RUN mkdir -p /tmp/hf_cache && chown -R user:user /tmp/hf_cache
RUN chown -R user:user /app

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files and set ownership
COPY --chown=user:user backend/ .

# Switch to non-root user
USER user

# Download the sentence-transformer model at build time
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Hugging Face exposes port 7860 by default
EXPOSE 7860

# Bind to PORT env var or fall back to 7860
CMD ["sh", "-c", "gunicorn app.main:app --bind 0.0.0.0:${PORT:-7860} --worker-class uvicorn.workers.UvicornWorker --workers 2 --timeout 120 --keep-alive 5"]
