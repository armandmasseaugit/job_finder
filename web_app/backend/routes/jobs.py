from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

# UPDATED: Changed from S3 to Azure Blob Storage
from web_app.backend.services.azure_storage import get_likes as get_likes_
from web_app.backend.services.azure_storage import get_offers as get_offers_
from web_app.backend.services.azure_storage import get_relevance as get_relevance_
from web_app.backend.services.azure_storage import update_like

# DEPRECATED: S3 imports disabled
# from web_app.backend.services.s3 import get_likes as get_likes_
# from web_app.backend.services.s3 import get_offers as get_offers_
# from web_app.backend.services.s3 import get_relevance as get_relevance_
# from web_app.backend.services.s3 import update_like

router = APIRouter()


# Pydantic models
class UserStats(BaseModel):
    total_jobs: int
    liked_jobs: int
    disliked_jobs: int


class JobOffer(BaseModel):
    reference: str
    name: str
    company_name: str
    url: str
    logo_url: Optional[str] = None
    publication_date: str
    remote: Optional[str] = None
    city: Optional[str] = None
    relevance_score: Optional[float] = None
    description_preview: Optional[str] = None


@router.get("/offers", response_model=list[JobOffer])
def get_offers(
    date_filter: Optional[str] = None,
    sort_by: str = "date",
    search: Optional[str] = None,
):
    """Get job offers with filtering and sorting"""
    offers = get_offers_()
    relevance_scores = get_relevance_()

    # Convert to job offer format and add relevance scores
    job_offers = []
    for offer in offers:
        # Add relevance score if available
        ref = offer.get("reference", "")
        relevance_score = relevance_scores.get(ref, 0.0) if relevance_scores else 0.0

        job_offer = {
            "reference": ref,
            "name": offer.get("name", ""),
            "company_name": offer.get("company_name", ""),
            "url": offer.get("url", ""),
            "logo_url": offer.get("logo_url", ""),
            "publication_date": offer.get("publication_date", ""),
            "remote": offer.get("remote", ""),
            "city": offer.get("city", ""),
            "relevance_score": relevance_score,
            "description_preview": offer.get("description_preview", ""),
        }
        job_offers.append(job_offer)

    # Apply search filter
    if search:
        search_lower = search.lower()
        job_offers = [
            job
            for job in job_offers
            if (
                search_lower in job["name"].lower()
                or search_lower in job["company_name"].lower()
                or search_lower in job.get("description_preview", "").lower()
            )
        ]

    # Apply sorting
    if sort_by == "relevance":
        job_offers.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    else:  # sort by date (default)
        job_offers.sort(key=lambda x: x.get("publication_date", ""), reverse=True)

    return [JobOffer(**job) for job in job_offers]


@router.get("/stats", response_model=UserStats)
def get_user_stats():
    """Get user statistics"""
    offers = get_offers_()
    likes = get_likes_()

    total_jobs = len(offers)
    liked_jobs = len([k for k, v in likes.items() if v == "like"]) if likes else 0
    disliked_jobs = len([k for k, v in likes.items() if v == "dislike"]) if likes else 0

    return UserStats(
        total_jobs=total_jobs, liked_jobs=liked_jobs, disliked_jobs=disliked_jobs
    )


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
