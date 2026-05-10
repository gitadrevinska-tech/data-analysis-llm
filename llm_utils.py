"""
llm_utils.py — OpenRouter API izsaukums.
"""
import requests
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_URL

def ask_llm(system: str, user: str, max_tokens: int = 1000) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": OPENROUTER_MODEL,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    }
    resp = requests.post(OPENROUTER_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
