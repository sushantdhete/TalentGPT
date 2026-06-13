"""
TalentGPT - Main API Router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    jobs, candidates, rankings, chat, analytics
)

api_router = APIRouter()

api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["Candidates"])
api_router.include_router(rankings.router, prefix="/rankings", tags=["Rankings"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
