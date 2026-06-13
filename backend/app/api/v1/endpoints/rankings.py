"""
TalentGPT - Rankings API
Trigger multi-agent ranking for a job
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid

router = APIRouter()


class RankingRequest(BaseModel):
    job_id: str
    candidate_ids: Optional[List[str]] = None  # None = rank all
    force_recompute: bool = False


class RankingResponse(BaseModel):
    job_id: str
    total_candidates: int
    rankings: List[Dict[str, Any]]
    computed_at: str


@router.post("/compute/{job_id}")
async def compute_rankings(
    job_id: str,
    background_tasks: BackgroundTasks,
    force: bool = False
):
    """
    Trigger multi-agent ranking computation for a job.
    Runs asynchronously — poll /status/{job_id} for progress.
    """
    task_id = str(uuid.uuid4())
    
    # In production: push to Celery queue
    # background_tasks.add_task(run_ranking_pipeline, job_id, task_id)
    
    return {
        "task_id": task_id,
        "job_id": job_id,
        "status": "queued",
        "message": "Ranking pipeline queued. 6 AI agents analyzing candidates.",
        "estimated_time_seconds": 30,
    }


@router.get("/{job_id}")
async def get_rankings(
    job_id: str,
    page: int = 1,
    page_size: int = 20,
    min_score: float = 0,
    sort_by: str = "final_fit_score",
):
    """Get ranked candidates for a job with filtering and pagination."""
    
    # In production: fetch from DB
    # For demo: return mock data structure
    return {
        "job_id": job_id,
        "total": 150,
        "page": page,
        "page_size": page_size,
        "rankings": [],
        "summary": {
            "avg_fit_score": 67.3,
            "top_score": 94.2,
            "shortlist_count": 12,
            "strong_match_count": 28,
        }
    }


@router.get("/{job_id}/candidate/{candidate_id}")
async def get_candidate_ranking_detail(job_id: str, candidate_id: str):
    """Get full ranking detail for a specific candidate including explanations."""
    return {
        "job_id": job_id,
        "candidate_id": candidate_id,
        "rank": 1,
        "final_fit_score": 91.5,
        "agent_scores": {
            "skill_match": 95.0,
            "experience": 88.0,
            "behavior": 82.0,
            "learning": 94.0,
            "leadership": 78.0,
            "culture_fit": 88.0,
        },
        "strengths": [
            "Expert-level Python and ML skills matching all required skills",
            "5+ years of directly relevant NLP/LLM experience",
            "High learning velocity — adopted 3 new frameworks in past year"
        ],
        "weaknesses": [
            "Limited formal team management experience",
            "No exposure to the FinTech domain specifically"
        ],
        "risks": ["May be overqualified — risk of leaving for senior role"],
        "missing_skills": ["Kubernetes", "Spark"],
        "growth_potential": "High",
        "recruiter_summary": "Exceptional technical candidate with deep ML expertise and proven track record building production AI systems. Minor gaps in leadership and specific domain knowledge are offset by exceptional learning velocity. Strong hire for IC roles with growth potential.",
        "predictions": {
            "interview_success": 0.89,
            "offer_acceptance": 0.72,
            "retention_18mo": 0.81,
            "high_performer": 0.85,
            "leadership_potential": 0.68,
        }
    }


@router.post("/{job_id}/candidate/{candidate_id}/feedback")
async def submit_feedback(
    job_id: str,
    candidate_id: str,
    feedback: Dict[str, Any]
):
    """Submit recruiter feedback to train the learning loop."""
    
    valid_types = ["liked", "shortlisted", "rejected", "hired", "interviewed"]
    feedback_type = feedback.get("type")
    
    if feedback_type not in valid_types:
        raise HTTPException(400, f"Invalid feedback type. Must be one of: {valid_types}")
    
    # In production: save to DB and trigger model retraining
    return {
        "status": "recorded",
        "feedback_type": feedback_type,
        "message": f"Feedback recorded. TalentGPT will learn from this to improve future rankings.",
        "learning_signal": "positive" if feedback_type in ["liked", "shortlisted", "hired"] else "negative"
    }


@router.get("/{job_id}/export")
async def export_rankings(job_id: str, format: str = "json"):
    """Export ranked candidate list for submission."""
    
    # This would generate the hackathon submission file
    return {
        "format": format,
        "download_url": f"/files/rankings_{job_id}.{format}",
        "generated_at": "2024-01-01T00:00:00Z"
    }
