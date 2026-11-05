"""Find public pages about a contractor with Perplexity (decision D12).

Only the citation URLs are used. The answer text is never stored or shown,
because a generated answer is not evidence.
"""
from __future__ import annotations

import logging

import requests

log = logging.getLogger(__name__)
TIMEOUT_S = 30


def find_source_urls(api_key: str, model: str, name: str, city: str | None, state: str | None) -> list[str]:
    place = ", ".join(p for p in (city, state) if p)
    question = (
        f"Which public web pages name the owner, president or another decision-maker of the roofing "
        f"contractor '{name}' in {place}? Cite the pages."
    )
    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "user", "content": question}]},
            timeout=TIMEOUT_S,
        )
    except requests.RequestException as exc:
        log.info("Perplexity request failed: %s", type(exc).__name__)
        return []
    if resp.status_code != 200:
        log.info("Perplexity returned HTTP %s", resp.status_code)
        return []
    data = resp.json()
    urls = [u for u in data.get("citations") or [] if isinstance(u, str) and u.startswith("http")]
    return urls[:3]
