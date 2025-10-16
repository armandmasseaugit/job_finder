"""CV matching routes for FastAPI."""

import logging
from typing import List, Dict, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse

from ..services.cv_matching import get_cv_matcher

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cv", tags=["cv-matching"])


@router.post("/upload")
async def upload_cv_and_match(
    cv_file: UploadFile = File(...),
    top_k: int = Form(20),
    min_score: float = Form(0.3)
) -> JSONResponse:
    """Upload CV file and get matching jobs.
    
    Args:
        cv_file: CV file (PDF, DOCX, TXT)
        top_k: Number of top matches to return (default: 20)
        min_score: Minimum similarity score (0.0-1.0, default: 0.3)
        
    Returns:
        JSONResponse: CV text and matching jobs with scores
    """
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.doc', '.txt'}
        file_extension = cv_file.filename.split('.')[-1].lower() if cv_file.filename else ''
        
        if f'.{file_extension}' not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        file_content = await cv_file.read()
        
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Get CV matcher and process
        matcher = get_cv_matcher()
        
        try:
            cv_text, matches = matcher.process_cv_file_and_match(
                file_content=file_content,
                filename=cv_file.filename,
                top_k=top_k,  # Enlever la limite de 50
                min_score=min_score
            )
            
            return JSONResponse(content={
                "success": True,
                "filename": cv_file.filename,
                "cv_text_length": len(cv_text),
                "cv_text_preview": cv_text[:200] + "..." if len(cv_text) > 200 else cv_text,
                "cv_text_full": cv_text,  # Include full text for explanations
                "total_matches": len(matches),
                "matches": matches,
                "search_params": {
                    "top_k": top_k,
                    "min_score": min_score
                }
            })
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing CV upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during CV processing")


@router.post("/match-text")
async def match_cv_text(
    cv_text: str,
    top_k: int = 20,
    min_score: float = 0.3
) -> JSONResponse:
    """Match CV text directly (without file upload).
    
    Args:
        cv_text: CV text content
        top_k: Number of top matches to return
        min_score: Minimum similarity score
        
    Returns:
        JSONResponse: Matching jobs with scores
    """
    try:
        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="CV text cannot be empty")
        
        # Get CV matcher and find matches
        matcher = get_cv_matcher()
        
        matches = matcher.find_matching_jobs(
            cv_text=cv_text,
            top_k=top_k,  # Enlever la limite de 50
            min_score=min_score
        )
        
        return JSONResponse(content={
            "success": True,
            "cv_text_length": len(cv_text),
            "total_matches": len(matches),
            "matches": matches,
            "search_params": {
                "top_k": top_k,
                "min_score": min_score
            }
        })
        
    except Exception as e:
        logger.error(f"Error matching CV text: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during CV matching")


@router.post("/explain-match")
async def explain_cv_match(
    cv_text: str = Form(...),
    job_reference: str = Form(...),
    top_n_words: int = Form(10)
) -> JSONResponse:
    """Explain why a CV matches a specific job using perturbation analysis.
    
    Args:
        cv_text: The CV text to analyze
        job_reference: Reference ID of the job to explain match for
        top_n_words: Number of most important words to return (default: 10)
        
    Returns:
        JSONResponse: Detailed explanation of match with word importance
    """
    try:
        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="CV text cannot be empty")
        
        if not job_reference.strip():
            raise HTTPException(status_code=400, detail="Job reference cannot be empty")
        
        # Get CV matcher and explain match
        matcher = get_cv_matcher()
        
        explanation = matcher.explain_match(
            cv_text=cv_text,
            job_reference=job_reference,
            top_n_words=top_n_words
        )
        
        return JSONResponse(content={
            "success": True,
            "explanation": explanation,
            "analysis_type": "perturbation_analysis",
            "methodology": "Each word is removed from CV and impact on similarity score is measured"
        })
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error explaining CV match: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during match explanation")


@router.get("/stats")
async def get_cv_matching_stats() -> JSONResponse:
    """Get CV matching service statistics.
    
    Returns:
        JSONResponse: ChromaDB collection stats and service status
    """
    try:
        matcher = get_cv_matcher()
        stats = matcher.get_collection_stats()
        
        return JSONResponse(content={
            "success": True,
            "stats": stats,
            "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
            "supported_formats": [".pdf", ".docx", ".doc", ".txt"]
        })
        
    except Exception as e:
        logger.error(f"Error getting CV matching stats: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Could not retrieve CV matching statistics",
                "stats": {
                    "total_jobs": 0,
                    "status": f"error: {e}"
                }
            }
        )