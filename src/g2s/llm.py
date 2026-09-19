"""OpenAI-compatible chat client. One code path for Ollama and hosted providers."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

from g2s.config import settings


class LLMError(RuntimeError):
    """The provider failed or returned something unusable."""


def chat(prompt: str, system: str = "", timeout: int = 180) -> str:
    """One completion at temperature 0. Returns the message text."""
    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": prompt}
    ]
    body = json.dumps(
        {"model": settings.llm_model, "messages": messages, "temperature": 0, "stream": False}
    ).encode()
    request = urllib.request.Request(
        f"{settings.llm_base_url}/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {settings.llm_api_key}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise LLMError(str(error)) from error
    try:
        return payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as error:
        raise LLMError(f"unexpected response: {str(payload)[:200]}") from error


def extract_sparql(text: str) -> str:
    """Pull the query out of whatever the model wrapped it in (fences, prose, both)."""
    fenced = re.search(r"```(?:sparql)?\s*(.+?)```", text, re.DOTALL | re.IGNORECASE)
    body = fenced.group(1) if fenced else text
    # drop any chatter before the query actually starts
    start = re.search(r"(?im)^\s*(PREFIX|BASE|SELECT|ASK|CONSTRUCT|DESCRIBE)\b", body)
    return (body[start.start() :] if start else body).strip()
