from fastapi import APIRouter, Query
from web_app.backend.services.s3 import (
    get_offers as get_offers_,
    get_likes as get_likes_,
    get_relevance as get_relevance_,
    update_like,
)


router = APIRouter()


@router.get("/offers")
def get_offers():
    return get_offers_()


@router.get("/likes")
def get_likes():
    return get_likes_()


@router.get("/relevance")
def get_relevance():
    return get_relevance_()


@router.post("/likes/{job_id}")
def like_job(job_id: str, feedback: str = Query(...)):
    update_like(job_id, feedback)
    return {"status": "ok"}
