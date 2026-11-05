"""Run insight generation outside the request (decision D11).

The save request returns at once. A small thread pool generates the insight
and writes the result. The lead row is never changed by this module.
"""
from __future__ import annotations

import logging
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from ..db import session_scope
from ..models import Lead, LeadInsight
from . import generator, perplexity, website

log = logging.getLogger(__name__)

STALE_AFTER = timedelta(days=30)
# A job that runs longer than this is treated as lost (for example after a restart).
LOST_AFTER = timedelta(minutes=5)
DECISION_WORDS = re.compile(r"\b(owner|president|founder|ceo|principal|general manager|vice president)\b", re.I)

_executor: ThreadPoolExecutor | None = None
_config = None


def init_insight_runner(config) -> None:
    global _executor, _config
    _config = config
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=config.insight_workers, thread_name_prefix="insight")


def effective_status(insight: LeadInsight | None, prospect_retrieved_at: datetime, now: datetime | None = None) -> str:
    """The status that the UI shows: missing, generating, ready, failed or stale."""
    now = now or datetime.now(timezone.utc)
    if insight is None:
        return "missing"
    if insight.status == "generating":
        if insight.started_at and now - insight.started_at > LOST_AFTER:
            return "failed"
        return "generating"
    if insight.status == "ready" and insight.generated_at:
        if prospect_retrieved_at > insight.generated_at or now - insight.generated_at > STALE_AFTER:
            return "stale"
    return insight.status


def effective_error(insight: LeadInsight | None, status: str) -> str | None:
    if status == "failed" and insight is not None and insight.status == "generating":
        return "Insight generation did not finish. Retry."
    return insight.error if insight is not None and status == "failed" else None


def mark_generating(session, lead: Lead, now: datetime | None = None) -> bool:
    """Set the insight to generating. Return False when a job already runs (prevents duplicate jobs)."""
    now = now or datetime.now(timezone.utc)
    insight = lead.insight
    if insight is None:
        insight = LeadInsight(lead_id=lead.id, status="generating", attempts=0)
        session.add(insight)
        lead.insight = insight
    elif effective_status(insight, lead.prospect.retrieved_at, now) == "generating":
        return False
    insight.status = "generating"
    insight.error = None
    insight.started_at = now
    insight.attempts = (insight.attempts or 0) + 1
    return True


def submit(lead_id: int) -> None:
    _executor.submit(_run_safely, lead_id)


def _run_safely(lead_id: int) -> None:
    try:
        run(lead_id)
    except Exception:  # noqa: BLE001 - the job must always leave a final status
        log.exception("Insight job crashed for lead %s", lead_id)
        _finish(lead_id, status="failed", error="Insight generation stopped because of an internal error. Retry.")


def _facts(p) -> dict:
    return {
        "name": p.name, "directory": p.directory, "profile_url": p.profile_url, "phone": p.phone,
        "website_url": p.website_url, "address": p.address, "city": p.city, "state": p.state,
        "distance_mi": float(p.distance_mi) if p.distance_mi is not None else None,
        "distinctions": p.distinctions, "specialties": p.specialties,
        "years_in_business": p.years_in_business, "about_text": p.about_text,
        "rating": float(p.rating) if p.rating is not None else None, "review_count": p.review_count,
    }


def run(lead_id: int) -> None:
    with session_scope() as s:
        lead = s.get(Lead, lead_id)
        facts = _facts(lead.prospect)

    cfg = _config
    if not cfg.openai_api_key:
        _finish(lead_id, status="ready", mode="template", content=generator.template_insight(facts))
        return

    pages = website.fetch_site(facts["website_url"]) if facts["website_url"] else []
    site_text = " ".join(p.text for p in pages)
    if cfg.perplexity_api_key and not DECISION_WORDS.search(site_text):
        for url in perplexity.find_source_urls(cfg.perplexity_api_key, cfg.perplexity_model,
                                               facts["name"], facts["city"], facts["state"]):
            page, _ = website.fetch_page(url, website._robots(url))
            if page:
                pages.append(page)

    allowed = [facts["profile_url"], *[p.url for p in pages]]
    try:
        raw = generator.call_openai(cfg.openai_api_key, cfg.openai_model,
                                    generator.build_user_message(facts, pages, allowed))
        content = generator.validate(raw, allowed, pages)
    except generator.InsightError as exc:
        _finish(lead_id, status="failed", error=str(exc))
        return
    _finish(lead_id, status="ready", mode="ai", content=content)


def _finish(lead_id: int, status: str, error: str | None = None, mode: str | None = None, content: dict | None = None):
    with session_scope() as s:
        insight = s.scalar(select(LeadInsight).where(LeadInsight.lead_id == lead_id))
        if insight is None:
            return
        insight.status = status
        insight.error = error
        if status == "ready":
            insight.mode = mode
            insight.content = content
            insight.generated_at = datetime.now(timezone.utc)
        # On failure the last good content stays, so a stale insight is not lost.
