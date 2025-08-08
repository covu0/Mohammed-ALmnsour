from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    question: str = Field(..., description="User's legal question in plain language")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction or country/state, if known")
    topic: Optional[str] = Field(None, description="High-level topic such as contracts, employment, IP, etc.")
    mode: Optional[str] = Field(None, description="Optional mode toggle (e.g., concise, detailed)")


class QueryResponse(BaseModel):
    answer: str
    disclaimer: str
    safe: bool
    provider: str