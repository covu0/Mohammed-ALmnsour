# AI Legal Advisor (Educational-Only)

This is a minimal web app that provides general, educational information about legal topics. It is not a substitute for advice from a qualified attorney and does not create an attorney-client relationship.

## Important Disclaimer
- This app is for **educational and informational purposes only**.
- It does **not** provide legal advice.
- **No attorney-client relationship** is formed by using this app.
- Laws vary by jurisdiction and change over time. Always consult a licensed attorney for your specific situation.

## Features
- Web UI to ask legal questions with optional jurisdiction and topic.
- API endpoint `/api/answer` that returns an answer with an explicit disclaimer.
- Safe prompting to avoid specific legal advice and encourage consulting a lawyer.
- Works in two modes:
  - "mock" mode (no API key): returns a templated educational response with disclaimers.
  - LLM-backed mode (OpenAI, if `OPENAI_API_KEY` is present): adds a model-generated educational summary with safety controls.

## Quickstart

1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) (Optional) Provide an LLM API key

```bash
export OPENAI_API_KEY=YOUR_KEY_HERE
# Optional (defaults to gpt-4o-mini, if available to your key)
export OPENAI_MODEL=gpt-4o-mini
```

4) Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5) Open the app
- Navigate to `http://localhost:8000/static/` in your browser.

## API

- POST `/api/answer`
  - Request body:
    ```json
    {
      "question": "string",
      "jurisdiction": "string (optional)",
      "topic": "string (optional)",
      "mode": "string (optional)"
    }
    ```
  - Response body:
    ```json
    {
      "answer": "string",
      "disclaimer": "string",
      "safe": true,
      "provider": "mock|openai"
    }
    ```

## Safety and Scope
- The system prompt steers the model to avoid providing specific or definitive legal advice, drafting binding documents, or predicting outcomes.
- The model is instructed to offer general information, highlight uncertainties, and recommend consulting a licensed attorney.

## Development Notes
- Static assets are served from `app/static/`.
- If no `OPENAI_API_KEY` is found in the environment, the service operates in mock mode.
- You can customize prompts and providers in `app/llm.py`.