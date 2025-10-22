FROM job-finder-base:latest

WORKDIR /app

# Copy requirements spécifiques FastAPI
COPY web_app/backend/requirements.txt /app/requirements.txt

# Installer les dépendances supplémentaires FastAPI
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

# Copy project
COPY web_app/ /app/web_app/
COPY conf/ /app/conf/

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "web_app.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
