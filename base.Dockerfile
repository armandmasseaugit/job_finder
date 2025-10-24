FROM python:3.12-slim as base

# Définir les variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python lourdes communes
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir \
        torch \
        pandas \
        numpy \
        chromadb \
        sentence-transformers \
        scikit-learn \
        azure-storage-blob \
        azure-identity \
        redis \
        python-dotenv \
        spacy \
        PyPDF2 \
        pdfplumber \
        python-docx

# Télécharger le modèle spaCy français
RUN python -m spacy download fr_core_news_sm

WORKDIR /app
