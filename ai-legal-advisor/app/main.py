import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .schemas import QueryRequest, QueryResponse
from .llm import LegalAdvisorLLM


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="AI Legal Advisor (Educational)", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

llm = LegalAdvisorLLM()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "provider": llm.provider}


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse(url="/static/")


@app.post("/api/answer", response_model=QueryResponse)
async def answer(req: QueryRequest) -> QueryResponse:
    try:
        payload = req.model_dump()
        result = await llm.generate_answer(payload)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))