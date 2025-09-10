FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system deps (for PyTorch, sentence-transformers, pdfplumber, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    poppler-utils \
    git \
    libopenblas-dev \
    libomp-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies first (better for caching)
COPY requirements.txt ./ 
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
