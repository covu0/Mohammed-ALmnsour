import os
from typing import List, Tuple
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

_client = None

def _get_client():
    global _client
    if _client is not None:
        return _client
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI  # type: ignore
        _client = OpenAI(api_key=OPENAI_API_KEY)
        return _client
    except Exception:
        return None

SYSTEM_PROMPT = (
    "أنت مساعد قانوني سعودي مختص في مخالفات المرور.\n"
    "اكتب مسودات عربية رسمية موجزة، مع الاستشهاد بمقتطفات من المراجع المعطاة فقط.\n"
    "لا تفترض معلومات غير موجودة. إن كانت المراجع غير كافية، اذكر ذلك صراحة.\n"
)


def draft_objection_letter(payload: BaseModel, kb_hits: List[str]) -> Tuple[str, List[str], float]:
    user_desc = "\n".join([
        f"رقم اللوحة: {payload.plate_number}" if payload.plate_number else "",
        f"رمز المخالفة: {payload.violation_code}" if payload.violation_code else "",
        f"وصف المخالفة: {payload.violation_desc}" if payload.violation_desc else "",
        f"الموقع: {payload.location}" if payload.location else "",
        f"التاريخ: {payload.date}" if payload.date else "",
        f"تفاصيل إضافية: {payload.extra_context}" if payload.extra_context else "",
    ])

    context = "\n\n".join([f"- {c}" for c in kb_hits])

    client = _get_client()
    if client is None:
        # Fallback: template-based draft without calling LLM
        template = (
            "سعادة الجهة المختصة،\n\n"
            "الموضوع: طلب الاعتراض على مخالفة مرورية\n\n"
            f"أفيدكم بأنني أتقدم بطلب الاعتراض على المخالفة الموضحة أدناه:\n\n{user_desc}\n\n"
            "ملخص الواقعة: \nتم ضبط المخالفة المشار إليها، وأبين بأن هناك أسبابًا تستدعي إعادة النظر، استنادًا إلى المقتطفات التالية من المراجع:\n\n"
            f"{context}\n\n"
            "وبناءً عليه أطلب من جهتكم الموقرة مراجعة المخالفة واتخاذ ما يلزم.\n\n"
            "المرفقات: صور/مستندات داعمة.\n\n"
            "درجة الثقة: 0.4 — مُولّد دون نموذج لغوي بسبب تعذّر الاتصال."
        )
        return template, kb_hits[:3], 0.4

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (
            "المراجع:\n" + context + "\n\n" +
            "بيانات القضية:\n" + user_desc + "\n\n" +
            "اكتب مسودة خطاب اعتراض موجه إلى الجهة المختصة، باللهجة الرسمية السعودية،\n"
            "تتضمن: (١) بيانات صاحب الطلب، (٢) ملخص الواقعة، (٣) أسانيد نظامية مختصرة مع اقتباس المراجع، (٤) طلب الإلغاء أو المراجعة، (٥) قائمة مرفقات.\n"
            "أعد أيضًا سطرين يوضحان درجة الثقة (0-1) وأسبابها."
        )}
    ]

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.2,
    )

    text = resp.choices[0].message.content or ""
    citations = [line.strip("- ") for line in text.splitlines() if line.strip().startswith("[") or line.strip().startswith("- ")]
    confidence = 0.6
    for line in text.splitlines():
        if "درجة الثقة" in line or "الثقة" in line:
            import re
            m = re.search(r"([01](?:\.\d+)?)", line)
            if m:
                try:
                    confidence = float(m.group(1))
                except Exception:
                    pass
            break

    return text, citations[:5], confidence