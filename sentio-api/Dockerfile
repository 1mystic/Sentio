FROM python:3.11-slim

WORKDIR /app

# Build tools for numpy / sentence-transformers compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download NLTK corpora so the first request isn't slow
RUN python -c "\
import nltk; \
nltk.download('punkt'); \
nltk.download('punkt_tab'); \
nltk.download('stopwords'); \
nltk.download('vader_lexicon')" || true

# Pre-download the embedding model used by RAG
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" || true

COPY . .

# HuggingFace Spaces requires port 7860
EXPOSE 7860

# Single worker — APScheduler and the singleton Supabase client are not safe across multiple processes
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
