"""Business logic for prospects and leads: response building and mutations."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import queries
from .errors import ApiError
from .models import Lead, Prospect
from .schemas import (
    LeadInfo,
    LeadList,
    LeadQuery,
    LeadSummary,
    LinkedListing,
    Overview,
    ProspectDetail,
    ProspectList,
    ProspectQuery,
    ProspectStats,
    ProspectSummary,
    ScoreItem,
)
from .scoring import tier_for, top_reason

FOLLOW_UP_DAYS = 14  # decision D12
STATUSES = ("new", "contacted", "qualified", "dismissed")
NOT_IN_PUBLIC_SOURCES = ["Decision-maker name", "Current supplier", "Purchase volume", "Project pipeline", "Crew size"]
FIELD_LABELS = {
    "phone": "Phone", "website_url": "Website", "address": "Street address", "about_text": "About text",
    "years_in_business": "Years in business", "distance_mi": "Distance", "rating": "Google rating",
    "review_count": "Review count",
}


def _f(v) -> float | None:
    return float(v) if v is not None else None


def _link(p: Prospect | None) -> LinkedListing | None:
    return LinkedListing(prospect_id=p.id, directory=p.directory) if p else None


def _saved_via(p: Prospect, by_key: dict[str, Lead]) -> LinkedListing | None:
    lead = by_key.get(p.phone_digits or "")
    if lead and lead.prospect_id != p.id:
        return LinkedListing(prospect_id=lead.prospect_id, directory=lead.prospect.directory)
    return None


def summarize_prospects(session: Session, prospects: list[Prospect]) -> list[ProspectSummary]:
    twin_map = queries.twins(session, prospects)
    by_key = queries.saved_leads_by_key(session, {p.phone_digits for p in prospects if p.phone_digits})
    return [
        ProspectSummary(
            id=p.id, directory=p.directory, name=p.name, city=p.city, state=p.state, phone=p.phone,
            distance_mi=_f(p.distance_mi), rating=_f(p.rating), review_count=p.review_count,
            score=p.score.score, tier=tier_for(p.score.score), top_reason=top_reason(p.score.breakdown),
            has_website=bool(p.website_url), saved_lead_id=p.lead.id if p.lead else None,
            also_listed_in=_link(twin_map.get(p.id)), saved_via=_saved_via(p, by_key),
        )
        for p in prospects
    ]


def list_prospects(session: Session, q: ProspectQuery) -> ProspectList:
    rows, total = queries.prospect_page(session, q)
    return ProspectList(items=summarize_prospects(session, rows), total=total, page=q.page, page_size=q.page_size)


def prospect_detail(session: Session, prospect_id: int) -> ProspectDetail:
    p = queries.prospect_with_everything(session, prospect_id)
    if p is None:
        raise ApiError(404, "not_found", "This prospect does not exist.")
    twin = queries.twins(session, [p]).get(p.id)
    by_key = queries.saved_leads_by_key(session, {p.phone_digits} if p.phone_digits else set())
    unknown = [label for field, label in FIELD_LABELS.items() if getattr(p, field) in (None, "")]
    if not p.distinctions:
        unknown.append("GAF distinctions")
    lead = p.lead
    return ProspectDetail(
        id=p.id, directory=p.directory, gaf_source_id=p.gaf_source_id, profile_url=p.profile_url, name=p.name,
        phone=p.phone, website_url=p.website_url, address=p.address, city=p.city, state=p.state,
        about_text=p.about_text, years_in_business=p.years_in_business, distance_mi=_f(p.distance_mi),
        rating=_f(p.rating), review_count=p.review_count, distinctions=p.distinctions, specialties=p.specialties,
        retrieved_at=p.retrieved_at, score=p.score.score, tier=tier_for(p.score.score),
        score_breakdown=[ScoreItem(**i) for i in p.score.breakdown], scored_at=p.score.scored_at,
        unknown_fields=unknown, not_in_public_sources=NOT_IN_PUBLIC_SOURCES,
        also_listed_in=_link(twin), saved_via=_saved_via(p, by_key),
        lead=LeadInfo(
            id=lead.id, status=lead.status, saved_at=lead.saved_at, status_changed_at=lead.status_changed_at,
        ) if lead else None,
    )


def save_prospect(session: Session, prospect_id: int) -> tuple[ProspectDetail, bool]:
    """Save a prospect as a lead. Return (detail, created). Saving the same prospect again is harmless."""
    p = queries.prospect_with_everything(session, prospect_id)
    if p is None:
        raise ApiError(404, "not_found", "This prospect does not exist.")
    if p.lead is not None:
        return prospect_detail(session, prospect_id), False
    key = p.phone_digits
    session.add(Lead(prospect_id=p.id, company_key=key, status="new"))
    try:
        session.commit()
    except IntegrityError:
        # The unique indexes decide races: one lead per prospect and one per company (D8).
        session.rollback()
        existing = queries.saved_leads_by_key(session, {key} if key else set()).get(key or "")
        if existing is not None and existing.prospect_id != prospect_id:
            raise ApiError(409, "company_already_saved",
                           "This company is already saved through its other GAF listing.",
                           {"prospect_id": existing.prospect_id, "directory": existing.prospect.directory})
        return prospect_detail(session, prospect_id), False
    # The session keeps the prospect loaded with lead = None (expire_on_commit is off).
    # Expire it so the response includes the new lead.
    session.expire_all()
    return prospect_detail(session, prospect_id), True


def _lead_or_404(session: Session, lead_id: int) -> Lead:
    lead = session.get(Lead, lead_id)
    if lead is None:
        raise ApiError(404, "not_found", "This lead does not exist.")
    return lead


def update_status(session: Session, lead_id: int, status: str) -> ProspectDetail:
    lead = _lead_or_404(session, lead_id)
    if lead.status != status:
        lead.status = status
        lead.status_changed_at = datetime.now(timezone.utc)
    session.commit()
    return prospect_detail(session, lead.prospect_id)


def is_follow_up_due(status: str, status_changed_at: datetime, now: datetime) -> bool:
    """Decision D12: Contacted, and no status change for FOLLOW_UP_DAYS or more."""
    return status == "contacted" and now - status_changed_at >= timedelta(days=FOLLOW_UP_DAYS)


def _lead_summary(lead: Lead, now: datetime) -> LeadSummary:
    p = lead.prospect
    return LeadSummary(
        lead_id=lead.id, prospect_id=p.id, name=p.name, city=p.city, state=p.state, directory=p.directory,
        phone=p.phone, score=p.score.score, tier=tier_for(p.score.score), status=lead.status,
        status_changed_at=lead.status_changed_at, saved_at=lead.saved_at, distance_mi=_f(p.distance_mi),
        top_reason=top_reason(p.score.breakdown),
        follow_up_due=is_follow_up_due(lead.status, lead.status_changed_at, now),
    )


def _sort_key(s: LeadSummary):
    return (-s.score, s.name, s.lead_id)


# Each order ends with lead_id, so pages never repeat or skip a lead.
LEAD_SORTS = {
    "priority": _sort_key,
    "recently_saved": lambda s: (-s.saved_at.timestamp(), s.lead_id),
    "oldest_status_change": lambda s: (s.status_changed_at.timestamp(), s.lead_id),
}


def list_leads(session: Session, q: LeadQuery) -> LeadList:
    now = datetime.now(timezone.utc)
    # The directory filter runs in SQL. Counts then describe the chosen directory.
    summaries = [_lead_summary(l, now) for l in queries.all_leads(session, q.directory)]
    # Counts describe all saved leads. The table total describes the filtered result.
    status_counts = {k: sum(1 for s in summaries if s.status == k) for k in STATUSES}
    queue_counts = {
        "first_contact": sum(1 for s in summaries if s.status == "new"),
        "follow_up_due": sum(1 for s in summaries if s.follow_up_due),
    }
    items = summaries
    if q.scope == "active":
        items = [s for s in items if s.status != "dismissed"]
    elif q.scope == "dismissed":
        items = [s for s in items if s.status == "dismissed"]
    if q.queue == "first_contact":
        items = [s for s in items if s.status == "new"]
    elif q.queue == "follow_up_due":
        items = [s for s in items if s.follow_up_due]
    if q.status:
        items = [s for s in items if s.status == q.status]
    if q.q:
        needle = q.q.strip().lower()
        items = [s for s in items if needle in s.name.lower() or needle in (s.city or "").lower()]
    if q.tier:
        items = [s for s in items if s.tier == q.tier]
    items.sort(key=LEAD_SORTS[q.sort])
    start = (q.page - 1) * q.page_size
    return LeadList(items=items[start:start + q.page_size], total=len(items), page=q.page, page_size=q.page_size,
                    status_counts=status_counts, queue_counts=queue_counts, total_saved=len(summaries))


def prospect_stats(session: Session, directory: str | None = None) -> ProspectStats:
    base = queries.stats(session, directory)
    return ProspectStats(high=base["tiers"]["high"], saved=len(queries.all_leads(session, directory)),
                         high_unsaved=queries.count_high_unsaved(session, directory), **base)


def overview(session: Session, directory: str | None = None) -> Overview:
    now = datetime.now(timezone.utc)
    summaries = [_lead_summary(l, now) for l in queries.all_leads(session, directory)]
    active = [s for s in summaries if s.status != "dismissed"]
    counts = {k: sum(1 for s in summaries if s.status == k) for k in STATUSES}
    contacted = counts["contacted"] + counts["qualified"]
    return Overview(
        saved=len(active), not_contacted=counts["new"], contacted=contacted, qualified=counts["qualified"],
        dismissed=counts["dismissed"], contacted_pct=round(100 * contacted / len(active)) if active else 0,
        follow_up_days=FOLLOW_UP_DAYS,
        call_next=sorted([s for s in active if s.status == "new"], key=_sort_key)[:5],
        follow_up=sorted([s for s in active if s.follow_up_due], key=lambda s: s.status_changed_at)[:5],
        top_unsaved=summarize_prospects(session, queries.top_unsaved(session, directory)),
        snapshot_retrieved_at=queries.stats(session, directory)["snapshot_retrieved_at"],
    )
