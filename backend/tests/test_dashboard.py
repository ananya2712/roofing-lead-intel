"""Overview and Saved-lead counts compared with database rows; call lists; follow-up timing."""
from datetime import timedelta

import pytest

from conftest import sql

STATUSES = ("new", "contacted", "qualified", "dismissed")


def db_counts(engine, directory=None):
    q = "SELECT l.status, count(*) FROM leads l JOIN prospects p ON p.id = l.prospect_id"
    if directory:
        q += " WHERE p.directory = :d"
    q += " GROUP BY l.status"
    rows = dict(sql(engine, q, d=directory))
    return {s: rows.get(s, 0) for s in STATUSES}


def save_with_status(client, pid, status):
    lead_id = client.post(f"/api/v1/prospects/{pid}/save").get_json()["lead"]["id"]
    if status != "new":
        client.patch(f"/api/v1/leads/{lead_id}/status", json={"status": status})
    return lead_id


@pytest.mark.parametrize("directory", [None, "residential", "commercial"])
def test_counts_agree_with_database_for_every_status(client, engine, test_prospects, directory):
    for sid, status in zip(("UI1", "UI2", "UI3", "SAVE6"), STATUSES):
        save_with_status(client, test_prospects[sid], status)
    c = db_counts(engine, directory)
    q = f"?directory={directory}" if directory else ""
    ov = client.get(f"/api/v1/overview{q}").get_json()
    leads = client.get(f"/api/v1/leads{q}{'&' if q else '?'}scope=all").get_json()
    active = c["new"] + c["contacted"] + c["qualified"]
    assert ov["saved"] == active                                   # dismissed not counted
    assert ov["not_contacted"] == c["new"]
    assert ov["contacted"] == c["contacted"] + c["qualified"]
    assert ov["qualified"] == c["qualified"] and ov["dismissed"] == c["dismissed"]
    assert ov["contacted_pct"] == (round(100 * ov["contacted"] / active) if active else 0)
    assert leads["status_counts"] == c
    assert leads["total_saved"] == sum(c.values())


def test_active_scope_hides_dismissed_and_dismissed_scope_shows_only_them(client, test_prospects):
    d = save_with_status(client, test_prospects["UI2"], "dismissed")
    n = save_with_status(client, test_prospects["UI3"], "new")
    active = {i["lead_id"] for i in client.get("/api/v1/leads?q=zztest&page_size=100").get_json()["items"]}
    dismissed = {i["lead_id"] for i in client.get("/api/v1/leads?q=zztest&scope=dismissed&page_size=100").get_json()["items"]}
    assert n in active and d not in active
    assert dismissed == {d}


def test_empty_pipeline_has_no_division_by_zero(client, engine):
    empty = [d for d in ("residential", "commercial") if sum(db_counts(engine, d).values()) == 0]
    if not empty:
        pytest.skip("Both directories have saved leads in the demo data, so no empty pipeline exists.")
    ov = client.get(f"/api/v1/overview?directory={empty[0]}").get_json()
    assert ov["saved"] == 0 and ov["contacted_pct"] == 0 and ov["call_next"] == []


def test_first_contact_queue_lists_new_leads(client, test_prospects):
    n = save_with_status(client, test_prospects["UI1"], "new")
    c = save_with_status(client, test_prospects["UI2"], "contacted")
    ids = {i["lead_id"] for i in client.get("/api/v1/leads?queue=first_contact&q=zztest").get_json()["items"]}
    assert n in ids and c not in ids


def test_follow_up_starts_at_exactly_14_days_and_same_status_does_not_reset(client, engine, test_prospects):
    lead_id = save_with_status(client, test_prospects["UI1"], "contacted")

    def due():
        items = client.get("/api/v1/leads?queue=follow_up_due&q=zztest").get_json()["items"]
        return lead_id in {i["lead_id"] for i in items}

    sql(engine, "UPDATE leads SET status_changed_at = now() - interval '14 days' + interval '1 minute' WHERE id = :i", i=lead_id)
    assert not due()
    sql(engine, "UPDATE leads SET status_changed_at = now() - interval '14 days' - interval '1 minute' WHERE id = :i", i=lead_id)
    assert due()
    ov = client.get("/api/v1/overview").get_json()
    assert lead_id in {i["lead_id"] for i in ov["follow_up"]} or len(ov["follow_up"]) == 5

    stamp = sql(engine, "SELECT status_changed_at FROM leads WHERE id = :i", i=lead_id)[0][0]
    client.patch(f"/api/v1/leads/{lead_id}/status", json={"status": "contacted"})   # same status again
    assert sql(engine, "SELECT status_changed_at FROM leads WHERE id = :i", i=lead_id)[0][0] == stamp
    assert due()

    client.patch(f"/api/v1/leads/{lead_id}/status", json={"status": "qualified"})   # real change resets
    assert sql(engine, "SELECT status_changed_at > :s FROM leads WHERE id = :i", s=stamp, i=lead_id)[0][0]
    assert not due()


def test_lead_sorts_are_complete_and_stable(client, test_prospects):
    for sid in ("UI1", "UI2", "UI3", "SAVE6"):
        save_with_status(client, test_prospects[sid], "new")
    for sort in ("priority", "recently_saved", "oldest_status_change"):
        seen = []
        for page in (1, 2):
            seen += [i["lead_id"] for i in client.get(f"/api/v1/leads?q=zztest&sort={sort}&page_size=2&page={page}").get_json()["items"]]
        assert len(seen) == len(set(seen)) == 4, sort
    items = client.get("/api/v1/leads?q=zztest&sort=recently_saved").get_json()["items"]
    stamps = [i["saved_at"] for i in items]
    assert stamps == sorted(stamps, reverse=True)
