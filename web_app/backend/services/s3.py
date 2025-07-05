import os
import boto3
import json
from kedro.config import OmegaConfigLoader

# TODO: replace credentials source from local to kubernetes secrets
creds = (OmegaConfigLoader(
        conf_source="conf/",
        config_patterns={
            "credentials": ["**/credentials*", "credentials*", "credentials*/**"],
        },
    )).get("credentials")["aws_credentials"]

s3 = boto3.client(
    "s3",
    aws_access_key_id=creds["key"],
    aws_secret_access_key=creds["secret"],
    region_name=creds["client_kwargs"]["region_name"],
)

BUCKET = "wttj-scraping"

def get_likes():
    try:
        obj = s3.get_object(Bucket=BUCKET, Key="job_likes.json")
        return json.loads(obj["Body"].read().decode("utf-8"))
    except s3.exceptions.NoSuchKey:
        return {}
    except Exception:
        return {}


def get_relevance():
    try:
        obj = s3.get_object(Bucket=BUCKET, Key="scored_jobs.json")
        return json.loads(obj["Body"].read().decode("utf-8"))
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
