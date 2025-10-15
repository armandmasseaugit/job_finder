import json
import os
from io import BytesIO

import pandas as pd
import redis
import numpy as np
from azure.storage.blob import BlobServiceClient

# -------------------------
# AZURE BLOB STORAGE CONFIG
# -------------------------

blob_service_client = BlobServiceClient(
    account_url=f"https://{os.environ['AZURE_STORAGE_ACCOUNT_NAME']}.blob.core.windows.net",
    credential=os.environ["AZURE_STORAGE_ACCOUNT_KEY"],
)

# Azure Blob Storage containers mapping
CONTAINERS = {
    "jobs": "wttj-scraping",         # For wttj_jobs.xlsx, last_scrape.json, models
    "likes": "liked-jobs",           # For job_likes.json  
    "relevance": "relevance-scores"  # For scored_jobs.json
}

# -------------------------
# REDIS CONFIG
# -------------------------
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,
)

CACHE_TTL = 300  # secondes (5 minutes)


def get_offers():
    try:
        cache_key = "offers"
        if redis_client.exists(cache_key):
            return json.loads(redis_client.get(cache_key))
        
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINERS["jobs"], blob="wttj_jobs.xlsx"
        )
        buffer = BytesIO(blob_client.download_blob().readall())
        df = pd.read_excel(buffer)
        df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
        offers = df.to_dict(orient="records")

        redis_client.setex(cache_key, CACHE_TTL, json.dumps(offers))
        return offers
    except Exception:
        return []


def get_likes():
    try:
        cache_key = "job_likes"
        if redis_client.exists(cache_key):
            return json.loads(redis_client.get(cache_key))

        blob_client = blob_service_client.get_blob_client(
            container=CONTAINERS["likes"], blob="job_likes.json"
        )
        blob_data = blob_client.download_blob().readall()
        likes = json.loads(blob_data.decode("utf-8"))

        redis_client.setex(cache_key, CACHE_TTL, json.dumps(likes))
        return likes
    except Exception:
        return {}


def get_relevance():
    try:
        cache_key = "scored_jobs"
        if redis_client.exists(cache_key):
            return json.loads(redis_client.get(cache_key))

        blob_client = blob_service_client.get_blob_client(
            container=CONTAINERS["relevance"], blob="scored_jobs.json"
        )
        blob_data = blob_client.download_blob().readall()
        relevance = json.loads(blob_data.decode("utf-8"))

        redis_client.setex(cache_key, CACHE_TTL, json.dumps(relevance))
        return relevance
    except Exception:
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
        content_settings={'content_type': 'application/json'},
        overwrite=True
    )

    # MAJ du cache Redis
    redis_client.setex("job_likes", CACHE_TTL, json.dumps(existing_data))