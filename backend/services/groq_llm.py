from __future__ import annotations
"""
The ONLY LLM in Wingman — Groq llama-3.3-70b-versatile.
No Gemini. When GROQ_API_KEY is absent, each call returns the supplied
`mock` fallback so the whole product still runs for a demo.
"""
import json

from config import settings

try:
    from groq import Groq
    _client = Groq(api_key=settings.groq_api_key) if settings.has_groq else None
except Exception:
    _client = None

SYSTEM_DEFAULT = "You are Wingman, an AI passenger-rights expert. Be precise, legal, and clear."


async def llm(prompt: str, system: str = SYSTEM_DEFAULT,
              json_mode: bool = False, temperature: float = 0.2,
              mock: str | None = None) -> str:
    if not settings.has_groq or _client is None:
        return mock if mock is not None else ""
    kwargs = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 2048,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = _client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content


async def llm_json(prompt: str, system: str | None = None, mock: dict | list | None = None):
    if not settings.has_groq or _client is None:
        return mock if mock is not None else {}
    sys = system or "You are Wingman. Return only valid JSON, no explanation."
    raw = await llm(prompt, system=sys, json_mode=True)
    try:
        return json.loads(raw)
    except Exception:
        return mock if mock is not None else {}