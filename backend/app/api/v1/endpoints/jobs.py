from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
router = APIRouter()

class JobCreate(BaseModel):
    title: str
    company: str
    raw_text: str

@router.post("/")
async def create_job(job: JobCreate):
    """Create and analyze a new job description."""
    return {"id": "job-uuid", "title": job.title, "status": "analyzing"}

@router.get("/{job_id}")
async def get_job(job_id: str):
    return {"id": job_id, "title": "Senior ML Engineer"}

@router.post("/upload")
async def upload_jd(file: UploadFile = File(...)):
    content = await file.read()
    return {"filename": file.filename, "status": "queued"}
