from fastapi import APIRouter
router = APIRouter()

@router.get("/overview")
async def get_overview():
    return {"total_jobs": 0, "total_candidates": 0, "avg_fit_score": 0}

@router.get("/job/{job_id}")
async def get_job_analytics(job_id: str):
    return {"job_id": job_id, "metrics": {}}
