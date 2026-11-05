"""Deterministic lead-priority score, rule version v1 (decision D7).

The score uses GAF data only. The same prospect and the same effective time
always give the same result. AI output never changes the score.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

RULE_VERSION = "v1"
FRESHNESS_DAYS = 30
HIGH_MIN = 70
MEDIUM_MIN = 45

TOP_TIER = ("president's club", "master elite", "chairman's circle", "platinumelite", "platinum elite")
CERTIFIED_TIER = ("certified", "goldelite", "gold elite", "coatingspro")
SPECIALTY_WORDS = ("fortified", "metal", "solar", "coating")


@dataclass(frozen=True)
class ScoreInput:
    directory: str
    distance_mi: Decimal | float | None
    distinctions: list[str]
    specialties: list[str]
    phone: str | None
    website_url: str | None
    address: str | None
    city: str | None
    state: str | None
    retrieved_at: datetime


def tier_for(score: int) -> str:
    if score >= HIGH_MIN:
        return "high"
    if score >= MEDIUM_MIN:
        return "medium"
    return "low"


def _item(key: str, label: str, points: int, maximum: int, reason: str, unknown: bool = False) -> dict:
    return {"key": key, "label": label, "points": points, "max": maximum, "reason": reason, "unknown": unknown}


def _geographic(distance) -> dict:
    if distance is None:
        return _item("distance", "Distance from ZIP 10013", 0, 35, "Distance is unknown.", unknown=True)
    d = float(distance)
    if d <= 10:
        pts = 35
    elif d <= 25:
        pts = 22
    elif d <= 50:
        pts = 10
    else:
        pts = 0
    return _item("distance", "Distance from ZIP 10013", pts, 35, f"{d:.1f} mi from ZIP 10013.")


def _certification(distinctions: list[str]) -> dict:
    lowered = [d.lower() for d in distinctions]
    top = [d for d, low in zip(distinctions, lowered) if any(w in low for w in TOP_TIER)]
    if top:
        return _item("certification", "GAF certification tier", 20, 20, f"Top GAF tier: {top[0]}.")
    certified = [d for d, low in zip(distinctions, lowered) if any(w in low for w in CERTIFIED_TIER)]
    if certified:
        return _item("certification", "GAF certification tier", 12, 20, f"GAF certified: {certified[0]}.")
    if not distinctions:
        return _item("certification", "GAF certification tier", 0, 20, "No GAF distinction is listed.", unknown=True)
    return _item("certification", "GAF certification tier", 0, 20, "Listed distinctions are not certification tiers.")


def _roof_systems(directory: str, specialties: list[str]) -> dict:
    if directory == "residential":
        return _item("roof_systems", "Roof systems listed", 10, 10, "Listed in the GAF residential (steep-slope) directory.")
    if specialties:
        return _item("roof_systems", "Roof systems listed", 10, 10, f"Commercial technologies: {', '.join(specialties[:3])}.")
    return _item("roof_systems", "Roof systems listed", 0, 10, "Commercial roof technologies are not listed.", unknown=True)


def _specialty(distinctions: list[str], specialties: list[str]) -> dict:
    for value in [*specialties, *distinctions]:
        if any(w in value.lower() for w in SPECIALTY_WORDS):
            return _item("specialty", "Specialty roofing", 5, 5, f"Specialty: {value}.")
    return _item("specialty", "Specialty roofing", 0, 5, "No FORTIFIED, metal, solar or coatings specialty is listed.")


def _readiness(inp: ScoreInput, effective_time: datetime) -> list[dict]:
    items = [
        _item("phone", "Phone listed", 10, 10, "GAF lists a phone number.")
        if inp.phone else _item("phone", "Phone listed", 0, 10, "Phone number is unknown.", unknown=True),
        _item("website", "Website listed", 10, 10, "GAF links a company website.")
        if inp.website_url else _item("website", "Website listed", 0, 10, "Website is unknown.", unknown=True),
    ]
    full_address = bool(inp.address and inp.city and inp.state)
    items.append(
        _item("address", "Full address", 5, 5, "Street, city and state are listed.")
        if full_address else _item("address", "Full address", 0, 5, "Full address is unknown.", unknown=True)
    )
    age = effective_time - inp.retrieved_at
    fresh = age <= timedelta(days=FRESHNESS_DAYS)
    items.append(
        _item("freshness", "Data freshness", 5 if fresh else 0, 5,
              f"Retrieved {age.days} days ago (limit {FRESHNESS_DAYS} days).")
    )
    return items


def score_prospect(inp: ScoreInput, effective_time: datetime) -> tuple[int, list[dict]]:
    """Return (total, breakdown). Missing data gets 0 points and is marked unknown."""
    breakdown = [
        _geographic(inp.distance_mi),
        _certification(inp.distinctions),
        _roof_systems(inp.directory, inp.specialties),
        _specialty(inp.distinctions, inp.specialties),
        *_readiness(inp, effective_time),
    ]
    total = sum(i["points"] for i in breakdown)
    return total, breakdown


def top_reason(breakdown: list[dict]) -> str:
    """One line for the table: the categories that gave the most points."""
    earned = sorted((i for i in breakdown if i["points"] > 0), key=lambda i: (-i["points"], i["key"]))
    parts = []
    for i in earned[:3]:
        if i["key"] == "distance":
            parts.append(i["reason"].split(" from")[0])
        elif i["key"] == "certification":
            # "GAF Master Elite® - Certification" reads better without the type suffix.
            parts.append(i["reason"].split(": ", 1)[-1].rstrip(".").split(" - ")[0])
        else:
            parts.append(i["label"].lower())
    return ", ".join(parts) if parts else "No scoring signals found."
