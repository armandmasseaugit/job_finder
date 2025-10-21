FROM python:3.12-slim as base

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies (minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY web_app/backend/requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY web_app/ /app/web_app/
COPY src/ /app/src/
COPY conf/ /app/conf/

# Ensure app package is importable
ENV PYTHONPATH=/app

EXPOSE 8000

# Lightweight healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "web_app.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
