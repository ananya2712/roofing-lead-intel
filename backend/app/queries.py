"""Feature-specific database reads for prospects and leads."""
from __future__ import annotations

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from .models import Lead, Prospect, ProspectScore
from .scoring import HIGH_MIN, MEDIUM_MIN

TIER_RANGES = {"high": (HIGH_MIN, 101), "medium": (MEDIUM_MIN, HIGH_MIN), "low": (0, MEDIUM_MIN)}
CERT_POINTS = {"top": 20, "certified": 12, "none": 0}


def _order(stmt: Select, sort: str) -> Select:
    # Stable order with a tie-breaker (D7): score, distance, name, id.
    if sort == "distance":
        return stmt.order_by(Prospect.distance_mi.asc().nulls_last(), ProspectScore.score.desc(), Prospect.name, Prospect.id)
    if sort == "name":
        return stmt.order_by(Prospect.name, Prospect.id)
    return stmt.order_by(ProspectScore.score.desc(), Prospect.distance_mi.asc().nulls_last(), Prospect.name, Prospect.id)


def prospect_page(session: Session, q) -> tuple[list[Prospect], int]:
    stmt = select(Prospect).join(ProspectScore).outerjoin(Lead, Lead.prospect_id == Prospect.id)
    conds = []
    if q.q:
        like = f"%{q.q.strip()}%"
        conds.append(or_(Prospect.name.ilike(like), Prospect.city.ilike(like)))
    if q.directory:
        conds.append(Prospect.directory == q.directory)
    if q.tier:
        lo, hi = TIER_RANGES[q.tier]
        conds.append(and_(ProspectScore.score >= lo, ProspectScore.score < hi))
    if q.max_distance:
        conds.append(Prospect.distance_mi <= q.max_distance)
    if q.state:
        conds.append(Prospect.state == q.state.upper())
    if q.cert_tier:
        conds.append(ProspectScore.breakdown.contains([{"key": "certification", "points": CERT_POINTS[q.cert_tier]}]))
    if q.hide_saved:
        saved_keys = select(Lead.company_key).where(Lead.company_key.is_not(None))
        conds.append(Lead.id.is_(None))
        conds.append(or_(Prospect.phone_digits.is_(None), Prospect.phone_digits.not_in(saved_keys)))
    if conds:
        stmt = stmt.where(*conds)
    total = session.scalar(select(func.count()).select_from(stmt.subquery()))
    stmt = _order(stmt, q.sort).options(joinedload(Prospect.score), joinedload(Prospect.lead))
    rows = session.scalars(stmt.offset((q.page - 1) * q.page_size).limit(q.page_size)).unique().all()
    return list(rows), total or 0


def twins(session: Session, prospects: list[Prospect]) -> dict[int, Prospect]:
    """Map prospect id to its listing in the other directory (same phone number)."""
    keys = {p.phone_digits for p in prospects if p.phone_digits}
    if not keys:
        return {}
    others = session.scalars(select(Prospect).where(Prospect.phone_digits.in_(keys)).options(joinedload(Prospect.lead))).unique().all()
    by_key: dict[str, list[Prospect]] = {}
    for o in others:
        by_key.setdefault(o.phone_digits, []).append(o)
    out = {}
    for p in prospects:
        for o in by_key.get(p.phone_digits or "", []):
            if o.id != p.id and o.directory != p.directory:
                out[p.id] = o
                break
    return out


def saved_leads_by_key(session: Session, keys: set[str]) -> dict[str, Lead]:
    if not keys:
        return {}
    rows = session.scalars(select(Lead).where(Lead.company_key.in_(keys)).options(joinedload(Lead.prospect))).unique().all()
    return {r.company_key: r for r in rows}


def _in_directory(stmt: Select, directory: str | None) -> Select:
    """Residential / commercial filter, applied in SQL."""
    return stmt.where(Prospect.directory == directory) if directory else stmt


def all_leads(session: Session, directory: str | None = None) -> list[Lead]:
    """Saved leads for one directory or both. The saved set is representative-sized, so
    the list view applies the remaining time-based filters in memory."""
    stmt = (
        select(Lead)
        .join(Prospect, Lead.prospect_id == Prospect.id)
        .options(joinedload(Lead.prospect).joinedload(Prospect.score))
        .order_by(Lead.id)
    )
    return list(session.scalars(_in_directory(stmt, directory)).unique().all())


def prospect_with_everything(session: Session, prospect_id: int) -> Prospect | None:
    stmt = (
        select(Prospect)
        .where(Prospect.id == prospect_id)
        .options(joinedload(Prospect.score), joinedload(Prospect.lead))
    )
    return session.scalars(stmt).unique().one_or_none()


def stats(session: Session, directory: str | None = None) -> dict:
    """Counts for the KPI cards and charts. directories always covers both, for the toggle."""
    def count(*conds) -> int:
        stmt = select(func.count(Prospect.id)).select_from(Prospect).join(ProspectScore).where(*conds)
        return session.scalar(_in_directory(stmt, directory)) or 0

    tiers = {name: count(ProspectScore.score >= lo, ProspectScore.score < hi) for name, (lo, hi) in TIER_RANGES.items()}
    directories = dict(session.execute(select(Prospect.directory, func.count()).group_by(Prospect.directory)).all())
    bands = {
        "0-10": count(Prospect.distance_mi <= 10),
        "10-25": count(Prospect.distance_mi > 10, Prospect.distance_mi <= 25),
        "25-50": count(Prospect.distance_mi > 25, Prospect.distance_mi <= 50),
        "unknown": count(Prospect.distance_mi.is_(None)),
    }
    states = [st for st in session.scalars(_in_directory(select(Prospect.state).distinct(), directory).order_by(Prospect.state)) if st]
    retrieved = session.scalar(_in_directory(select(func.max(Prospect.retrieved_at)), directory))
    return {"total": count(), "tiers": tiers, "directories": directories, "distance_bands": bands,
            "states": states, "snapshot_retrieved_at": retrieved}


def _unsaved_high(stmt: Select, directory: str | None) -> Select:
    saved_keys = select(Lead.company_key).where(Lead.company_key.is_not(None))
    stmt = (
        stmt.join(ProspectScore)
        .outerjoin(Lead, Lead.prospect_id == Prospect.id)
        .where(Lead.id.is_(None), ProspectScore.score >= HIGH_MIN,
               or_(Prospect.phone_digits.is_(None), Prospect.phone_digits.not_in(saved_keys)))
    )
    return _in_directory(stmt, directory)


def top_unsaved(session: Session, directory: str | None = None, limit: int = 5) -> list[Prospect]:
    stmt = _unsaved_high(select(Prospect), directory).options(joinedload(Prospect.score))
    return list(session.scalars(_order(stmt, "score").limit(limit)).unique().all())


def count_high_unsaved(session: Session, directory: str | None = None) -> int:
    return session.scalar(_unsaved_high(select(func.count(Prospect.id)).select_from(Prospect), directory)) or 0
