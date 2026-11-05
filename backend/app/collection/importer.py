"""Normalize, deduplicate and store snapshot records, then score them.

A repeated import updates the GAF columns of the same row. It never touches
the leads table, so representative work stays intact.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ..models import Prospect, ProspectScore
from ..scoring import RULE_VERSION, ScoreInput, score_prospect
from .snapshot import SnapshotRecord, load_snapshot

log = logging.getLogger(__name__)

GAF_COLUMNS = (
    "profile_url", "name", "phone", "phone_digits", "website_url", "address", "city", "state",
    "about_text", "years_in_business", "distance_mi", "rating", "review_count",
    "distinctions", "specialties", "retrieved_at",
)


@dataclass
class ImportResult:
    file: str
    directory: str
    expected_total: int | None
    valid: int
    invalid: list[dict]
    inserted: int
    updated: int
    prospect_ids: list[int]

    @property
    def complete(self) -> bool:
        return self.expected_total is not None and self.valid == self.expected_total and not self.invalid


def phone_digits(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits if len(digits) == 10 else None


def _clean(text: str | None) -> str | None:
    if text is None:
        return None
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def normalize(rec: SnapshotRecord, directory: str) -> dict:
    street = _clean(rec.street)
    city = _clean(rec.city)
    state = _clean(rec.state)
    parts = [p for p in (street, city, " ".join(p for p in (state, _clean(rec.postal_code)) if p)) if p]
    return {
        "directory": directory,
        "gaf_source_id": rec.gaf_source_id.strip(),
        "profile_url": rec.profile_url,
        "name": _clean(rec.name),
        "phone": _clean(rec.phone),
        "phone_digits": phone_digits(rec.phone),
        "website_url": _clean(rec.website_url),
        "address": ", ".join(parts) if street else None,
        "city": city,
        "state": state.upper() if state else None,
        "about_text": _clean(rec.about_text),
        "years_in_business": _clean(rec.years_in_business),
        "distance_mi": rec.distance_mi,
        "rating": rec.rating,
        "review_count": rec.review_count,
        "distinctions": sorted({d.strip() for d in rec.distinctions if d and d.strip()}),
        "specialties": sorted({s.strip() for s in rec.specialties if s and s.strip()}),
        "retrieved_at": rec.retrieved_at,
    }


def import_file(session: Session, path: Path) -> ImportResult:
    snapshot, records, invalid = load_snapshot(path)
    rows = {}
    for rec in records:
        row = normalize(rec, snapshot.directory)
        rows[row["gaf_source_id"]] = row  # the same ID twice in one file keeps the last copy

    existing = set(
        session.scalars(
            select(Prospect.gaf_source_id).where(
                Prospect.directory == snapshot.directory,
                Prospect.gaf_source_id.in_(list(rows)),
            )
        )
    )
    if rows:
        stmt = insert(Prospect).values(list(rows.values()))
        stmt = stmt.on_conflict_do_update(
            constraint="uq_prospect_listing",
            set_={c: stmt.excluded[c] for c in GAF_COLUMNS},
        )
        session.execute(stmt)
    session.commit()
    ids = list(session.scalars(select(Prospect.id).where(
        Prospect.directory == snapshot.directory, Prospect.gaf_source_id.in_(list(rows)))))
    result = ImportResult(
        file=path.name,
        directory=snapshot.directory,
        expected_total=snapshot.expected_total,
        valid=len(rows),
        invalid=invalid,
        inserted=len(rows) - len(existing),
        updated=len(existing),
        prospect_ids=ids,
    )
    log.info("Imported %s: %s new, %s updated, %s invalid", path.name, result.inserted, result.updated, len(invalid))
    return result


def rescore_all(session: Session, effective_time: datetime | None = None, prospect_ids: list[int] | None = None) -> int:
    """Recalculate scores with an explicit effective time (UTC). prospect_ids limits the work to those rows."""
    now = effective_time or datetime.now(timezone.utc)
    count = 0
    stmt = select(Prospect)
    if prospect_ids is not None:
        stmt = stmt.where(Prospect.id.in_(prospect_ids))
    for p in session.scalars(stmt):
        total, breakdown = score_prospect(
            ScoreInput(
                directory=p.directory, distance_mi=p.distance_mi, distinctions=p.distinctions,
                specialties=p.specialties, phone=p.phone, website_url=p.website_url,
                address=p.address, city=p.city, state=p.state, retrieved_at=p.retrieved_at,
            ),
            now,
        )
        stmt = insert(ProspectScore).values(
            prospect_id=p.id, score=total, breakdown=breakdown, rule_version=RULE_VERSION, scored_at=now
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["prospect_id"],
            set_={"score": total, "breakdown": breakdown, "rule_version": RULE_VERSION, "scored_at": now},
        )
        session.execute(stmt)
        count += 1
    session.commit()
    return count
