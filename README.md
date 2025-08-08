# Saudi Traffic Violation Assistant (MVP)

Minimal MVP: generate Arabic objection letters for Saudi traffic violations with citations to references. Backend: FastAPI (Python). Frontend: simple HTML form. Knowledge base: markdown files in `kb/`.

## Features (MVP)
- Upload violation image/PDF or paste details
- Extract key fields (plate, violation code, location, date)
- Retrieve relevant references from KB (RAG)
- Draft Arabic objection letter with citations
- Human review step before export to PDF

## Stack
- Python 3.13, FastAPI, Uvicorn
- OpenAI GPT-4/5 (text + function calling)
- `whisperx` (optional) for audio, `pdfplumber`/`pytesseract` (optional) for OCR
- FAISS for retrieval

## Quickstart
1. Create `.env` with `OPENAI_API_KEY=...`
2. Install deps: `pip install -r requirements.txt`
3. Run API: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
4. Open frontend: visit `http://localhost:8000`

## Legal Notice
This is an informational assistant, not a law firm. Always have a licensed attorney review before submission. Jurisdiction: KSA.
