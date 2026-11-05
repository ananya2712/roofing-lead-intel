"""Read and validate a GAF snapshot file (decision D1).

A snapshot file holds records that were collected one time from the GAF
directory in a browser. This module validates the file. It does not write
to the database.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class SnapshotRecord(BaseModel):
    gaf_source_id: str = Field(min_length=1, max_length=32)
    profile_url: str
    name: str = Field(min_length=1)
    phone: str | None = None
    website_url: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    about_text: str | None = None
    years_in_business: str | None = None
    distance_mi: float | None = None
    rating: float | None = None
    review_count: int | None = None
    distinctions: list[str] = []
    specialties: list[str] = []
    retrieved_at: datetime

    @field_validator("profile_url")
    @classmethod
    def _gaf_url(cls, v: str) -> str:
        if not v.startswith("https://www.gaf.com/"):
            raise ValueError("profile_url must be a gaf.com URL")
        return v

    @field_validator("website_url")
    @classmethod
    def _http_url(cls, v: str | None) -> str | None:
        if v and not v.lower().startswith(("http://", "https://")):
            return None
        return v

    @field_validator("rating")
    @classmethod
    def _rating(cls, v: float | None) -> float | None:
        return v if v is None or 0 <= v <= 5 else None


class Snapshot(BaseModel):
    directory: str
    postal_code: str
    radius_mi: int
    search_url: str
    expected_total: int | None
    collected_at: datetime
    collection_method: str
    records: list[dict]

    @field_validator("directory")
    @classmethod
    def _directory(cls, v: str) -> str:
        if v not in ("residential", "commercial"):
            raise ValueError("directory must be residential or commercial")
        return v


def load_snapshot(path: Path) -> tuple[Snapshot, list[SnapshotRecord], list[dict]]:
    """Return the snapshot header, the valid records, and the invalid records with errors."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    snapshot = Snapshot.model_validate(raw)
    valid, invalid = [], []
    for i, rec in enumerate(snapshot.records):
        try:
            valid.append(SnapshotRecord.model_validate(rec))
        except Exception as exc:  # noqa: BLE001 - report every bad record, keep the good ones
            invalid.append({"index": i, "gaf_source_id": rec.get("gaf_source_id"), "error": str(exc)[:300]})
    return snapshot, valid, invalid
