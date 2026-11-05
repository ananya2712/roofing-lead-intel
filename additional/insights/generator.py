"""Generate and validate a short account-planning insight.

The model receives only collected facts and fetched page text. The server
then checks every source URL and every contact name against that input.
"""
from __future__ import annotations

import json
import logging
import re
import time

import requests

from .website import Page

log = logging.getLogger(__name__)
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
TIMEOUT_S = 60
MAX_ATTEMPTS = 2
DEFAULT_ROLE = "Owner or purchasing manager"


class InsightError(Exception):
    """A failure that the representative can retry."""


SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["why", "topics", "contact", "next_action", "sources"],
    "properties": {
        "why": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["text", "source_urls"],
                "properties": {"text": {"type": "string"}, "source_urls": {"type": "array", "items": {"type": "string"}}},
            },
        },
        "topics": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["topic", "reason"],
                "properties": {"topic": {"type": "string"}, "reason": {"type": "string"}},
            },
        },
        "contact": {
            "type": "object",
            "additionalProperties": False,
            "required": ["kind", "name", "role", "source_url", "explanation"],
            "properties": {
                "kind": {"type": "string", "enum": ["named", "role"]},
                "name": {"type": ["string", "null"]},
                "role": {"type": "string"},
                "source_url": {"type": ["string", "null"]},
                "explanation": {"type": "string"},
            },
        },
        "next_action": {"type": "string"},
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["url", "label"],
                "properties": {"url": {"type": "string"}, "label": {"type": "string"}},
            },
        },
    },
}

SYSTEM_PROMPT = """You help a sales representative of a roofing-materials distributor plan a first conversation with a roofing contractor.
Use ONLY the facts and page text in the user message. Rules:
- "why": 1 or 2 short sentences on why this contractor may be relevant to a distributor. Each sentence cites one or more URLs from the ALLOWED SOURCES list.
- A GAF listing, certification, rating or review count does NOT show purchase intent, demand or business size. Do not claim them.
- Do not invent contacts, crew sizes, projects, purchase history, product demand or buying intent.
- "topics": 2 or 3 roofing-material conversation topics that follow from the listed directory, distinctions, specialties or page text. Give a short reason for each.
- "contact": use kind "named" ONLY when a page text in the input states a person's name AND role at this company. Copy the name exactly and give that page URL. Otherwise use kind "role", name null, source_url null, and suggest the role to ask for.
- "next_action": one practical step the representative can take this week.
- "sources": the URLs you used, each from the ALLOWED SOURCES list, with a short label.
- Write short, plain sentences."""


def build_user_message(facts: dict, pages: list[Page], allowed: list[str]) -> str:
    page_blocks = "\n\n".join(f"PAGE {p.url}\n{p.text}" for p in pages) or "(no website pages were available)"
    return (
        f"FACTS FROM GAF (source {facts['profile_url']}):\n{json.dumps(facts, ensure_ascii=False, indent=1)}\n\n"
        f"WEBSITE AND PUBLIC PAGES:\n{page_blocks}\n\n"
        f"ALLOWED SOURCES:\n" + "\n".join(allowed)
    )


def call_openai(api_key: str, model: str, user_message: str) -> dict:
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_message}],
        "response_format": {"type": "json_schema", "json_schema": {"name": "lead_insight", "strict": True, "schema": SCHEMA}},
    }
    last_error = "unknown error"
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = requests.post(
                OPENAI_URL,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=TIMEOUT_S,
            )
        except requests.Timeout:
            last_error = f"The AI provider did not answer in {TIMEOUT_S} seconds."
        except requests.RequestException as exc:
            last_error = f"The AI provider could not be reached ({type(exc).__name__})."
        else:
            if resp.status_code == 200:
                choice = resp.json()["choices"][0]["message"]
                if choice.get("refusal"):
                    raise InsightError("The AI provider refused the request.")
                try:
                    return json.loads(choice["content"])
                except (TypeError, json.JSONDecodeError) as exc:
                    raise InsightError("The AI provider returned data that is not valid JSON.") from exc
            # Retry only failures that can recover.
            if resp.status_code not in (408, 429, 500, 502, 503, 504):
                raise InsightError(f"The AI provider rejected the request (HTTP {resp.status_code}).")
            last_error = f"The AI provider is busy or failed (HTTP {resp.status_code})."
        if attempt < MAX_ATTEMPTS:
            time.sleep(2 * attempt)
    raise InsightError(last_error)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def validate(content: dict, allowed: list[str], pages: list[Page]) -> dict:
    """Keep only supported claims. Raise InsightError when nothing supported remains."""
    allowed_set = set(allowed)
    why = []
    for item in content.get("why", [])[:2]:
        urls = [u for u in item.get("source_urls", []) if u in allowed_set]
        if urls and item.get("text", "").strip():
            why.append({"text": item["text"].strip(), "source_urls": urls})
    if not why:
        raise InsightError("The AI insight had no claim with a valid source.")

    topics = [t for t in content.get("topics", []) if t.get("topic", "").strip()][:3]
    if len(topics) < 2:
        raise InsightError("The AI insight had fewer than 2 conversation topics.")

    contact = content.get("contact") or {}
    page_text = {p.url: _norm(p.text) for p in pages}
    name = (contact.get("name") or "").strip()
    source = contact.get("source_url")
    named_ok = (
        contact.get("kind") == "named"
        and name
        and source in page_text
        and _norm(name) in page_text[source]
    )
    if named_ok:
        contact = {"kind": "named", "name": name, "role": contact.get("role") or "Unknown role",
                   "source_url": source, "explanation": contact.get("explanation", "")}
    else:
        contact = {
            "kind": "role",
            "name": None,
            "role": contact.get("role") if contact.get("kind") == "role" and contact.get("role") else DEFAULT_ROLE,
            "source_url": None,
            "explanation": "No fetched public page confirms a decision-maker's name and role.",
        }

    next_action = (content.get("next_action") or "").strip()
    if not next_action:
        raise InsightError("The AI insight had no next action.")

    used = {u for w in why for u in w["source_urls"]}
    if contact["source_url"]:
        used.add(contact["source_url"])
    sources = [s for s in content.get("sources", []) if s.get("url") in allowed_set]
    for url in used - {s["url"] for s in sources}:
        sources.append({"url": url, "label": "Source"})
    return {"why": why, "topics": topics, "contact": contact, "next_action": next_action, "sources": sources}


def template_insight(facts: dict) -> dict:
    """Rule-based insight for template mode (no OpenAI key). It contains no AI output."""
    gaf = facts["profile_url"]
    tier = next((d for d in facts.get("distinctions", [])), None)
    why = [{"text": f"{facts['name']} is listed in the GAF {facts['directory']} directory"
                    + (f" with the distinction {tier}." if tier else "."),
            "source_urls": [gaf]}]
    if facts["directory"] == "commercial":
        topics = [{"topic": "Low-slope membranes", "reason": "Listed in the GAF commercial directory."},
                  {"topic": "Roof coatings and accessories", "reason": "Common for commercial roof work."}]
    else:
        topics = [{"topic": "Architectural shingles", "reason": "Listed in the GAF residential directory."},
                  {"topic": "Underlayment and ventilation", "reason": "Parts of a complete residential roof system."}]
    phone = facts.get("phone")
    return {
        "why": why,
        "topics": topics,
        "contact": {"kind": "role", "name": None, "role": DEFAULT_ROLE, "source_url": None,
                    "explanation": "Template mode does not search for names."},
        "next_action": f"Call {phone} and ask for the {DEFAULT_ROLE.lower()}." if phone
        else "Find a phone number on the GAF profile, then call.",
        "sources": [{"url": gaf, "label": "GAF profile"}],
    }
