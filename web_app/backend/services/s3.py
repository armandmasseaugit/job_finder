import os
from io import BytesIO
import numpy as np
import pandas as pd
import boto3
import json
import redis

# -------------------------
# AWS S3 CONFIG
# -------------------------

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ["AWS_REGION"],
)

BUCKET = "wttj-scraping"

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
        obj = s3.get_object(Bucket=BUCKET, Key="wttj_jobs.xlsx")
        buffer = BytesIO(obj["Body"].read())
        df = pd.read_excel(buffer)
        df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
        offers = df.to_dict(orient="records")

        redis_client.setex(cache_key, CACHE_TTL, json.dumps(offers))
        return offers
    except s3.exceptions.NoSuchKey:
        return []
    except Exception:
        return []


def get_likes():
    try:
        cache_key = "job_likes"
        if redis_client.exists(cache_key):
            return json.loads(redis_client.get(cache_key))

        obj = s3.get_object(Bucket=BUCKET, Key="job_likes.json")
        likes = json.loads(obj["Body"].read().decode("utf-8"))

        redis_client.setex(cache_key, CACHE_TTL, json.dumps(likes))
        return likes
    except s3.exceptions.NoSuchKey:
        return {}
    except Exception:
        return {}


def get_relevance():
    try:
        cache_key = "scored_jobs"
        if redis_client.exists(cache_key):
            return json.loads(redis_client.get(cache_key))

        obj = s3.get_object(Bucket=BUCKET, Key="scored_jobs.json")
        relevance = json.loads(obj["Body"].read().decode("utf-8"))

        redis_client.setex(cache_key, CACHE_TTL, json.dumps(relevance))
        return relevance
    except s3.exceptions.NoSuchKey:
        return {}
    except Exception:
        return {}


def update_like(job_ref: str, feedback: str):
    try:
        obj = s3.get_object(Bucket=BUCKET, Key="job_likes.json")
        existing_data = json.loads(obj["Body"].read().decode("utf-8"))
    except s3.exceptions.NoSuchKey:
        existing_data = {}
    except Exception:
        return

    existing_data[job_ref] = feedback

    s3.put_object(
        Bucket=BUCKET,
        Key="job_likes.json",
        Body=json.dumps(existing_data, indent=2),
        ContentType="application/json",
    )

    # MAJ du cache Redis
    redis_client.setex("job_likes", CACHE_TTL, json.dumps(existing_data))
