import json
import os
from io import BytesIO

import numpy as np
import pandas as pd
import redis
from azure.storage.blob import BlobServiceClient, ContentSettings

# -------------------------
# AZURE BLOB STORAGE CONFIG
# -------------------------

blob_service_client = BlobServiceClient(
    account_url=f"https://{os.environ['AZURE_STORAGE_ACCOUNT_NAME']}.blob.core.windows.net",
    credential=os.environ["AZURE_STORAGE_ACCOUNT_KEY"],
)

# Azure Blob Storage containers mapping
CONTAINERS = {
    "jobs": "wttj-scraping",  # For wttj_jobs.parquet, last_scrape.json, models
    "likes": "liked-jobs",  # For job_likes.json
    "relevance": "relevance-scores",  # For scored_jobs.json
}

# -------------------------
# REDIS CONFIG
# -------------------------
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True,
    )
    # Test Redis connection
    redis_client.ping()
    REDIS_AVAILABLE = True
    print("✅ Redis connection successful")
except Exception as e:
    print(f"⚠️ Redis not available: {e}")
    redis_client = None
    REDIS_AVAILABLE = False

CACHE_TTL = 300  # secondes (5 minutes)


def get_offers():
    try:
        cache_key = "offers"

        # Try cache first if Redis is available
        if REDIS_AVAILABLE and redis_client.exists(cache_key):
            return json.loads(redis_client.get(cache_key))

        blob_client = blob_service_client.get_blob_client(
            container=CONTAINERS["jobs"], blob="wttj_jobs.parquet"
        )
        buffer = BytesIO(blob_client.download_blob().readall())
        df = pd.read_parquet(buffer)

        # Convert problematic columns to proper types before to_dict()
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype(str)

        # Clean NaN/inf values properly
        df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
        df = df.where(pd.notnull(df), None)  # Extra safety for NaN

        offers = df.to_dict(orient="records")

        # Cache result if Redis is available
        if REDIS_AVAILABLE:
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(offers))

        return offers
    except Exception as e:
        print(f"Error getting offers: {e}")
        return []


def get_likes():
    try:
        cache_key = "job_likes"

        # Try cache first if Redis is available
        if REDIS_AVAILABLE and redis_client.exists(cache_key):
            return json.loads(redis_client.get(cache_key))

        blob_client = blob_service_client.get_blob_client(
            container=CONTAINERS["likes"], blob="job_likes.json"
        )
        blob_data = blob_client.download_blob().readall()
        likes = json.loads(blob_data.decode("utf-8"))

        # Cache result if Redis is available
        if REDIS_AVAILABLE:
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(likes))

        return likes
    except Exception as e:
        print(f"Error getting likes: {e}")
        return {}


def get_relevance():
    try:
        cache_key = "scored_jobs"

        # Try cache first if Redis is available
        if REDIS_AVAILABLE and redis_client.exists(cache_key):
            return json.loads(redis_client.get(cache_key))

        blob_client = blob_service_client.get_blob_client(
            container=CONTAINERS["relevance"], blob="scored_jobs.json"
        )
        blob_data = blob_client.download_blob().readall()
        relevance = json.loads(blob_data.decode("utf-8"))

        # Cache result if Redis is available
        if REDIS_AVAILABLE:
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(relevance))

        return relevance
    except Exception as e:
        print(f"Error getting relevance: {e}")
        return {}


def update_like(job_ref: str, feedback: str):
    try:
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINERS["likes"], blob="job_likes.json"
        )
        try:
            blob_data = blob_client.download_blob().readall()
            existing_data = json.loads(blob_data.decode("utf-8"))
        except Exception:
            existing_data = {}
    except Exception:
        existing_data = {}

    existing_data[job_ref] = feedback

    blob_client = blob_service_client.get_blob_client(
        container=CONTAINERS["likes"], blob="job_likes.json"
    )
    blob_client.upload_blob(
        data=json.dumps(existing_data, indent=2),
        content_settings=ContentSettings(content_type="application/json"),
        overwrite=True,
    )

    # MAJ du cache Redis
    if REDIS_AVAILABLE:
        redis_client.setex("job_likes", CACHE_TTL, json.dumps(existing_data))
