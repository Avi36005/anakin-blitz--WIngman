"""
The ONLY LLM in Wingman — Groq llama-3.3-70b-versatile.
No Gemini. Uses a POOL of Groq API keys and rotates to the next key on any
rate-limit / error, so a single key hitting its limit never breaks the app.
When no keys are configured, each call returns the supplied `mock` fallback.
"""
from __future__ import annotations

import json
import itertools

from config import settings

try:
    from groq import Groq
    _clients = [Groq(api_key=k) for k in settings.groq_keys]
except Exception:
    _clients = []

# Round-robin starting point that advances as keys get exhausted.
_cycle = itertools.cycle(range(len(_clients))) if _clients else None

SYSTEM_DEFAULT = "You are Wingman, an AI passenger-rights expert. Be precise, legal, and clear."


def _ordered_clients():
    """Yield clients starting at the current rotation offset, wrapping once."""
    if not _clients:
        return []
    start = next(_cycle)
    n = len(_clients)
    return [_clients[(start + i) % n] for i in range(n)]


async def llm(prompt: str, system: str = SYSTEM_DEFAULT,
              json_mode: bool = False, temperature: float = 0.2,
              mock: str | None = None) -> str:
    if not _clients:
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

    last_err = None
    for i, client in enumerate(_ordered_clients()):
        try:
            resp = client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content
        except Exception as e:  # rate limit / auth / transient — try next key
            last_err = e
            print(f"[groq] key #{i + 1} failed ({type(e).__name__}); rotating…")
            continue

    print(f"[groq] all {len(_clients)} keys failed: {last_err}")
    return mock if mock is not None else ""


async def llm_json(prompt: str, system: str | None = None, mock: dict | list | None = None):
    if not _clients:
        return mock if mock is not None else {}
    sys = system or "You are Wingman. Return only valid JSON, no explanation."
    raw = await llm(prompt, system=sys, json_mode=True)
    try:
        return json.loads(raw)
    except Exception:
        return mock if mock is not None else {}
