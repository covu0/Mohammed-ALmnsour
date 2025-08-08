import os
import json
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from ..services.rag import retrieve_references
from ..services.gpt import draft_objection_letter

load_dotenv()

router = APIRouter()

class DraftRequest(BaseModel):
    plate_number: Optional[str] = None
    violation_code: Optional[str] = None
    violation_desc: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    extra_context: Optional[str] = None

class DraftResponse(BaseModel):
    letter_ar: str
    citations: List[str]
    confidence: float

@router.post("/draft", response_model=DraftResponse)
async def draft(
    payload: DraftRequest,
):
    kb_hits = retrieve_references(query=json.dumps(payload.model_dump(exclude_none=True), ensure_ascii=False))
    if not kb_hits:
        raise HTTPException(status_code=400, detail="لم يتم العثور على مراجع كافية في قاعدة المعرفة.")

    letter, citations, confidence = draft_objection_letter(payload, kb_hits)
    return DraftResponse(letter_ar=letter, citations=citations, confidence=confidence)