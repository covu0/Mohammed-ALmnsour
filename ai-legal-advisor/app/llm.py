import os
from typing import Dict, Any
import httpx


SAFE_SYSTEM_PROMPT = (
    "You are an AI legal information assistant. You do NOT provide legal advice. "
    "You provide general, educational information only. You are not a lawyer and "
    "no attorney-client relationship is formed. Always include a brief disclaimer, "
    "highlight uncertainties, avoid definitive prescriptions, and encourage the user "
    "to consult a qualified attorney for their specific situation. If the user asks for "
    "instructions that constitute practicing law (e.g., drafting binding documents, "
    "predicting case outcomes, or advising on litigation strategy), respond with high-level "
    "educational context and recommend seeking professional counsel."
)

MOCK_TEMPLATE = (
    "Educational overview only (not legal advice).\n\n"
    "Key points to consider:\n"
    "- Laws vary by jurisdiction and may have changed.\n"
    "- Context matters; small facts can alter outcomes.\n"
    "- Consider speaking with a licensed attorney.\n\n"
    "General information about your question:\n{content}\n\n"
    "Next steps you might take (non-exhaustive):\n"
    "- Identify your jurisdiction and any relevant deadlines.\n"
    "- Collect documents and timeline of events.\n"
    "- Contact a local legal aid clinic or bar association referral service.\n"
)


class LegalAdvisorLLM:
    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.provider = "openai" if self.openai_api_key else "mock"

    async def generate_answer(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        question: str = payload.get("question", "").strip()
        jurisdiction: str = (payload.get("jurisdiction") or "").strip()
        topic: str = (payload.get("topic") or "").strip()
        mode: str = (payload.get("mode") or "").strip()

        if not question:
            return {
                "answer": "Please provide a clear question so I can share general, educational information.",
                "disclaimer": self._disclaimer(),
                "safe": True,
                "provider": self.provider,
            }

        # Minimal heuristic guardrails
        unsafe_phrases = [
            "draft a contract",
            "write a contract",
            "guarantee outcome",
            "guarantee win",
            "specific legal advice",
            "tell me what to do in court",
            "litigation strategy",
            "is this legal in my case",
        ]
        contains_sensitive = any(p in question.lower() for p in unsafe_phrases)

        if self.provider == "mock":
            content_summary = self._build_content_summary(question, jurisdiction, topic, mode, contains_sensitive)
            answer = MOCK_TEMPLATE.format(content=content_summary)
            return {
                "answer": answer,
                "disclaimer": self._disclaimer(),
                "safe": True,
                "provider": self.provider,
            }

        # OpenAI-backed mode via HTTP API (no SDK dependency)
        try:
            messages = [
                {"role": "system", "content": SAFE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": self._compose_user_message(question, jurisdiction, topic, mode, contains_sensitive),
                },
            ]
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.openai_model,
                        "messages": messages,
                        "temperature": 0.2,
                        "max_tokens": 800,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                content = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "I could not generate a response at this time.")
                )
        except Exception as e:
            content = (
                "I encountered an issue contacting the LLM provider. "
                "Here is a general, educational overview instead.\n\n" +
                self._build_content_summary(question, jurisdiction, topic, mode, contains_sensitive)
            )

        return {
            "answer": content,
            "disclaimer": self._disclaimer(),
            "safe": True,
            "provider": self.provider,
        }

    def _compose_user_message(
        self,
        question: str,
        jurisdiction: str,
        topic: str,
        mode: str,
        contains_sensitive: bool,
    ) -> str:
        parts = []
        parts.append("User question:")
        parts.append(question)
        if jurisdiction:
            parts.append(f"\nJurisdiction (optional): {jurisdiction}")
        if topic:
            parts.append(f"\nTopic (optional): {topic}")
        if mode:
            parts.append(f"\nMode (optional): {mode}")
        if contains_sensitive:
            parts.append(
                "\nNOTE: The question appears to request specific legal advice or drafting. "
                "Provide only general, high-level educational information and suggest speaking to a lawyer."
            )
        parts.append(
            "\nStructure your response as:\n"
            "- Brief summary (educational only)\n"
            "- Key considerations and variables\n"
            "- Potential next steps and resources\n"
            "Avoid definitive legal conclusions; emphasize consulting an attorney."
        )
        return "\n".join(parts)

    def _build_content_summary(
        self,
        question: str,
        jurisdiction: str,
        topic: str,
        mode: str,
        contains_sensitive: bool,
    ) -> str:
        summary_lines = []
        summary_lines.append(f"Question: {question}")
        if jurisdiction:
            summary_lines.append(f"Jurisdiction (provided): {jurisdiction}")
        if topic:
            summary_lines.append(f"Topic (provided): {topic}")
        if contains_sensitive:
            summary_lines.append(
                "Note: The question seems to seek specific legal advice or document drafting. "
                "Only high-level educational context is provided here."
            )
        summary_lines.append(
            "Common considerations may include the governing law, deadlines, required notices, "
            "contract terms or statutes that could apply, and factual nuances."
        )
        return "\n".join(summary_lines)

    def _disclaimer(self) -> str:
        return (
            "This response is for educational purposes only and is not legal advice. "
            "No attorney-client relationship is formed. Laws vary by jurisdiction and change "
            "over time. Consult a licensed attorney for advice on your specific situation."
        )