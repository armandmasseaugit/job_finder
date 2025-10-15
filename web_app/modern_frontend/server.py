#!/usr/bin/env python3
"""
Modern Frontend Server for Job Finder
Serves the HTMX frontend and provides API endpoints
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import logging
from datetime import datetime, timedelta
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Job Finder Modern Frontend",
    description="HTMX-based modern frontend for Job Finder application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Pydantic models
class CVUploadResponse(BaseModel):
    success: bool
    extracted_text: str
    message: str

class CVMatchRequest(BaseModel):
    cv_text: str

class JobOffer(BaseModel):
    reference: str
    name: str
    company_name: str
    url: str
    logo_url: str
    publication_date: str
    remote: str
    city: str
    relevance_score: float
    description_preview: str
    match_score: Optional[float] = None
    match_reasons: Optional[List[str]] = None
    confidence_level: Optional[str] = None

class UserStats(BaseModel):
    total_jobs: int
    liked_jobs: int
    disliked_jobs: int

# Mock data store (in production, this would be a database)
MOCK_JOBS = [
    {
        "reference": "job_001",
        "name": "Senior Python Developer",
        "company_name": "TechCorp",
        "url": "https://example.com/job1",
        "logo_url": "https://via.placeholder.com/64x64/3B82F6/FFFFFF?text=TC",
        "publication_date": "2024-01-15",
        "remote": "hybrid",
        "city": "Paris",
        "relevance_score": 8.5,
        "description_preview": "We are looking for a Senior Python Developer to join our dynamic team. You will work on cutting-edge projects using Django, FastAPI, and modern Python frameworks..."
    },
    {
        "reference": "job_002", 
        "name": "ML Engineer",
        "company_name": "AI Startup",
        "url": "https://example.com/job2",
        "logo_url": "https://via.placeholder.com/64x64/10B981/FFFFFF?text=AI",
        "publication_date": "2024-01-14",
        "remote": "full_remote",
        "city": "Lyon",
        "relevance_score": 9.2,
        "description_preview": "Join our AI team to develop machine learning models for production. Experience with TensorFlow, PyTorch, and MLOps required..."
    },
    {
        "reference": "job_003",
        "name": "Frontend Developer React",
        "company_name": "WebAgency",
        "url": "https://example.com/job3", 
        "logo_url": "https://via.placeholder.com/64x64/8B5CF6/FFFFFF?text=WA",
        "publication_date": "2024-01-13",
        "remote": "office",
        "city": "Marseille",
        "relevance_score": 7.8,
        "description_preview": "We need a talented React developer to build amazing user interfaces. Knowledge of TypeScript, Next.js, and modern CSS frameworks required..."
    }
]

MOCK_STATS = {
    "total_jobs": len(MOCK_JOBS),
    "liked_jobs": 12,
    "disliked_jobs": 5
}

# Routes

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main index.html file"""
    index_path = os.path.join(frontend_dir, "index.html")
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend not found")

@app.get("/app.js")
async def serve_app_js():
    """Serve the app.js file"""
    js_path = os.path.join(frontend_dir, "app.js")
    return FileResponse(js_path, media_type="application/javascript")

@app.get("/explore", response_class=HTMLResponse)
@app.get("/explore.html", response_class=HTMLResponse)
async def serve_explore():
    """Serve the explore page"""
    explore_path = os.path.join(frontend_dir, "explore.html")
    try:
        with open(explore_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Explore page not found")

@app.get("/cv-match", response_class=HTMLResponse)
@app.get("/cv_matching.html", response_class=HTMLResponse)
async def serve_cv_matching():
    """Serve the CV matching page"""
    cv_path = os.path.join(frontend_dir, "cv_matching.html")
    try:
        with open(cv_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="CV matching page not found")

@app.get("/stats", response_model=UserStats)
async def get_user_stats():
    """Get user statistics"""
    return UserStats(**MOCK_STATS)

@app.get("/offers", response_model=List[JobOffer])
async def get_offers(
    date_filter: Optional[str] = None,
    sort_by: str = "date",
    search: Optional[str] = None
):
    """Get job offers with filtering and sorting"""
    jobs = MOCK_JOBS.copy()
    
    # Apply date filter
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, "%Y-%m-%d")
            jobs = [
                job for job in jobs 
                if datetime.strptime(job["publication_date"], "%Y-%m-%d") >= filter_date
            ]
        except ValueError:
            logger.warning(f"Invalid date filter: {date_filter}")
    
    # Apply search filter
    if search:
        search_lower = search.lower()
        jobs = [
            job for job in jobs
            if (search_lower in job["name"].lower() or 
                search_lower in job["company_name"].lower() or
                search_lower in job["description_preview"].lower())
        ]
    
    # Apply sorting
    if sort_by == "relevance":
        jobs.sort(key=lambda x: x["relevance_score"], reverse=True)
    else:  # sort by date (default)
        jobs.sort(key=lambda x: x["publication_date"], reverse=True)
    
    return [JobOffer(**job) for job in jobs]

@app.post("/likes/{job_reference}")
async def handle_feedback(
    job_reference: str,
    feedback: str,
    source: str = "explore"
):
    """Handle like/dislike feedback for jobs"""
    if feedback not in ["like", "dislike"]:
        raise HTTPException(status_code=400, detail="Invalid feedback type")
    
    # In production, this would update the database
    logger.info(f"Feedback received: {feedback} for job {job_reference} from {source}")
    
    # Update mock stats
    if feedback == "like":
        MOCK_STATS["liked_jobs"] += 1
    else:
        MOCK_STATS["disliked_jobs"] += 1
    
    return {"success": True, "message": f"Feedback '{feedback}' recorded for job {job_reference}"}

@app.post("/cv/upload", response_model=CVUploadResponse)
async def upload_cv(cv_file: UploadFile = File(...)):
    """Upload and process CV file"""
    
    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/msword", 
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    ]
    
    if cv_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload PDF, DOC, DOCX, or TXT files."
        )
    
    # Validate file size (5MB max)
    content = await cv_file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")
    
    # Mock text extraction (in production, use libraries like PyPDF2, python-docx, etc.)
    mock_extracted_text = """
    John Doe
    Senior Software Engineer
    
    Experience:
    - 5 years Python development with Django and FastAPI
    - Machine Learning projects using TensorFlow and scikit-learn
    - Full-stack development with React and Vue.js
    - DevOps experience with Docker and Kubernetes
    
    Skills:
    - Python, JavaScript, TypeScript
    - Django, FastAPI, React, Vue.js
    - PostgreSQL, MongoDB
    - AWS, Docker, Kubernetes
    - Machine Learning, Data Analysis
    
    Education:
    - Master's in Computer Science
    """
    
    logger.info(f"CV uploaded: {cv_file.filename}, size: {len(content)} bytes")
    
    return CVUploadResponse(
        success=True,
        extracted_text=mock_extracted_text.strip(),
        message="CV processed successfully"
    )

@app.post("/cv/match", response_model=List[JobOffer])
async def match_cv(request: CVMatchRequest):
    """Find matching jobs based on CV content"""
    
    # Mock CV matching logic (in production, use ChromaDB similarity search)
    cv_text_lower = request.cv_text.lower()
    
    # Calculate mock match scores based on keyword overlap
    matched_jobs = []
    for job in MOCK_JOBS:
        job_text = f"{job['name']} {job['description_preview']}".lower()
        
        # Simple keyword matching for demo
        keywords = ["python", "django", "fastapi", "machine learning", "react", "javascript"]
        cv_keywords = [kw for kw in keywords if kw in cv_text_lower]
        job_keywords = [kw for kw in keywords if kw in job_text]
        
        common_keywords = set(cv_keywords) & set(job_keywords)
        match_score = len(common_keywords) / len(keywords) * 100 if keywords else 0
        
        if match_score > 20:  # Only include jobs with >20% match
            job_copy = job.copy()
            job_copy["match_score"] = round(match_score, 1)
            job_copy["match_reasons"] = [f"Matches {kw}" for kw in common_keywords]
            job_copy["confidence_level"] = "High" if match_score > 60 else "Medium" if match_score > 40 else "Low"
            matched_jobs.append(job_copy)
    
    # Sort by match score
    matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Return top 5 matches
    top_matches = matched_jobs[:5]
    
    logger.info(f"CV matching completed. Found {len(top_matches)} matches")
    
    return [JobOffer(**job) for job in top_matches]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info"
    )