FROM python:3.12-slim as base

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY kedro_requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

# Copy project
COPY src/ /app/src/
COPY conf/ /app/conf/
COPY pyproject.toml /app/

# Install editable project (if pyproject defines it)
RUN python -m pip install -e . || true

# Default command - designed to be overridden by k8s CronJob or compose
CMD ["kedro", "run"]
