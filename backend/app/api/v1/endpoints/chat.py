from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional
router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    job_id: Optional[str] = None
    session_id: Optional[str] = None
    history: List[Dict] = []

@router.post("/")
async def chat(payload: ChatMessage):
    return {"reply": "AI response here", "session_id": "session-uuid"}
