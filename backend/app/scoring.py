"""Lead-priority score, rule version v1 (decision D7).

Technique: an additive points model. Eight categories each give a fixed number
of points from one or two GAF fields. The total is 0–100. There is no machine
learning, no weighting by sales results and no AI. The same prospect and the
same effective time always give the same score, so a test can check every point.

Categories (maximum points):

  Fit for a roofing-materials distributor (70)
    distance        35  <= 10 mi: 35, <= 25 mi: 22, <= 50 mi: 10, farther: 0.
                        Delivery cost and rep travel depend most on distance.
    certification   20  Top GAF tier (Master Elite, President's Club,
                        PlatinumElite, Chairman's Circle): 20.
                        Other certified tier (Certified, GoldElite, CoatingsPro): 12.
    roof_systems    10  Residential listing: 10. Commercial listing with
                        roof technologies listed: 10. The products match ours.
    specialty        5  FORTIFIED, metal, solar or coating work: higher-value topics.

  Readiness: can a rep act today? (30)
    phone           10  GAF lists a phone number.
    website         10  GAF links a company website.
    address          5  Street, city and state are all present.
    freshness        5  Data read <= 30 days before the effective time.

Tiers: High >= 70, Medium 45–69, Low < 45.

Rules for missing data: a missing field gets 0 points and its item is marked
``unknown``, so the UI shows "Unknown" instead of a false zero.

Not scored on purpose: star rating and review count (reputation, and they
favor large firms), GAF search rank (GAF's order, not ours), years in business
(sources conflict) and the about text (free text that nobody checks).

Each category returns one breakdown item:
``{key, label, points, max, reason, unknown}``. The breakdown is stored with the
score, so the UI can explain every point.
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
    """The prospect fields that the rules read. Other fields cannot change the score."""

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
    """Return "high", "medium" or "low" for a total score."""
    if score >= HIGH_MIN:
        return "high"
    if score >= MEDIUM_MIN:
        return "medium"
    return "low"


def _item(key: str, label: str, points: int, maximum: int, reason: str, unknown: bool = False) -> dict:
    """Build one breakdown item. ``unknown`` means the source field is missing."""
    return {"key": key, "label": label, "points": points, "max": maximum, "reason": reason, "unknown": unknown}


def _geographic(distance) -> dict:
    """Distance band: 35 / 22 / 10 / 0 points. The bands are inclusive (10.0 mi gets 35)."""
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
    """Highest GAF tier found in the distinctions: top 20, certified 12, other 0."""
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
    """10 points when the listing shows roof systems that match the product lines."""
    # Every residential listing is a steep-slope roofer. A commercial listing
    # shows its systems only through the technologies it lists.
    if directory == "residential":
        return _item("roof_systems", "Roof systems listed", 10, 10, "Listed in the GAF residential (steep-slope) directory.")
    if specialties:
        return _item("roof_systems", "Roof systems listed", 10, 10, f"Commercial technologies: {', '.join(specialties[:3])}.")
    return _item("roof_systems", "Roof systems listed", 0, 10, "Commercial roof technologies are not listed.", unknown=True)


def _specialty(distinctions: list[str], specialties: list[str]) -> dict:
    """5 points for the first FORTIFIED, metal, solar or coating term found."""
    for value in [*specialties, *distinctions]:
        if any(w in value.lower() for w in SPECIALTY_WORDS):
            return _item("specialty", "Specialty roofing", 5, 5, f"Specialty: {value}.")
    return _item("specialty", "Specialty roofing", 0, 5, "No FORTIFIED, metal, solar or coatings specialty is listed.")


def _readiness(inp: ScoreInput, effective_time: datetime) -> list[dict]:
    """Phone (10), website (10), full address (5) and freshness (5)."""
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
    # The effective time is a parameter, not "now", so a rescore is repeatable.
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
