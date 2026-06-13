from fastapi import APIRouter, UploadFile, File
router = APIRouter()

@router.get("/")
async def list_candidates(page: int = 1, page_size: int = 20):
    return {"candidates": [], "total": 0, "page": page}

@router.get("/{candidate_id}")
async def get_candidate(candidate_id: str):
    return {"id": candidate_id}

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    return {"filename": file.filename, "status": "processing"}
