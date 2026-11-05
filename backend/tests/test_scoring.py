"""Scoring: totals, breakdowns, cutoffs, tiers, freshness, unknown vs zero, and score stability."""
from datetime import timedelta

import pytest

from conftest import COMMERCIAL, NOW, RESIDENTIAL, sql

CASES = [(s, score, tier) for s, _, score, tier in RESIDENTIAL + COMMERCIAL]


@pytest.mark.parametrize("sid,score,tier", CASES, ids=[c[0] for c in CASES])
def test_score_and_tier_match_hand_calculation(client, test_prospects, sid, score, tier):
    body = client.get(f"/api/v1/prospects/{test_prospects[sid]}").get_json()
    assert body["score"] == score
    assert body["tier"] == tier
    assert sum(i["points"] for i in body["score_breakdown"]) == score  # breakdown adds up to the total


@pytest.mark.parametrize("sid,points", [("D10", 35), ("D10P", 22), ("D25", 22), ("D25P", 10), ("D50", 10), ("DNONE", 0)])
def test_distance_cutoffs(client, test_prospects, sid, points):
    items = client.get(f"/api/v1/prospects/{test_prospects[sid]}").get_json()["score_breakdown"]
    dist = next(i for i in items if i["key"] == "distance")
    assert dist["points"] == points
    assert dist["unknown"] is (sid == "DNONE")


def test_tier_boundaries_70_69_45_44(client, test_prospects):
    tiers = {s: client.get(f"/api/v1/prospects/{test_prospects[s]}").get_json() for s in ("T70", "T69", "T45", "T44")}
    assert [(tiers[s]["score"], tiers[s]["tier"]) for s in ("T70", "T69", "T45", "T44")] == [
        (70, "high"), (69, "medium"), (45, "medium"), (44, "low")]


def test_freshness_boundary_at_30_days(app, engine, test_prospects):
    from app.collection.importer import rescore_all
    from app.db import session_scope

    pid = test_prospects["D10"]
    retrieved = sql(engine, "SELECT retrieved_at FROM prospects WHERE id = :i", i=pid)[0][0]

    def freshness_at(t):
        with app.app_context(), session_scope() as s:
            rescore_all(s, t, [pid])
        bd = sql(engine, "SELECT breakdown FROM prospect_scores WHERE prospect_id = :i", i=pid)[0][0]
        return next(i["points"] for i in bd if i["key"] == "freshness")

    try:
        assert freshness_at(retrieved + timedelta(days=30)) == 5
        assert freshness_at(retrieved + timedelta(days=30, seconds=1)) == 0
    finally:
        with app.app_context(), session_scope() as s:
            rescore_all(s, NOW, [pid])


def test_unknown_is_distinct_from_zero(client, test_prospects):
    zero = client.get(f"/api/v1/prospects/{test_prospects['ZERO']}").get_json()
    unknown = client.get(f"/api/v1/prospects/{test_prospects['D10']}").get_json()
    assert zero["rating"] == 0.0 and zero["review_count"] == 0
    assert "Google rating" not in zero["unknown_fields"]
    assert unknown["rating"] is None and unknown["review_count"] is None
    assert {"Google rating", "Review count", "Phone", "Website", "Street address"} <= set(unknown["unknown_fields"])
    web = next(i for i in unknown["score_breakdown"] if i["key"] == "website")
    assert web["points"] == 0 and web["unknown"] is True


def test_commercial_roof_systems_need_technologies(client, test_prospects):
    def roof(s):
        bd = client.get(f"/api/v1/prospects/{test_prospects[s]}").get_json()["score_breakdown"]
        return next(i for i in bd if i["key"] == "roof_systems")
    assert roof("CNOTECH")["points"] == 0 and roof("CNOTECH")["unknown"]
    assert roof("CTECH")["points"] == 10


def test_saving_and_status_changes_do_not_change_score(client, test_prospects):
    pid = test_prospects["SAVE1"]
    before = client.get(f"/api/v1/prospects/{pid}").get_json()
    lead_id = client.post(f"/api/v1/prospects/{pid}/save").get_json()["lead"]["id"]
    for status in ("contacted", "qualified", "dismissed"):
        after = client.patch(f"/api/v1/leads/{lead_id}/status", json={"status": status}).get_json()
        assert (after["score"], after["score_breakdown"]) == (before["score"], before["score_breakdown"])
