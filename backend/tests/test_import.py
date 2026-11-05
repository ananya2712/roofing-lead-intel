"""Snapshot import through the real CLI command: duplicates, updates, saved work, invalid records."""
import json

from conftest import rec, snapshot, sql


def run_import(app, folder):
    return app.test_cli_runner().invoke(args=["import-snapshot", "--dir", str(folder)])


def test_import_twice_creates_no_duplicates(app, engine, tmp_path):
    (tmp_path / "gaf_residential_t.json").write_text(json.dumps(snapshot("residential", [rec("IMP1"), rec("IMP2")])))
    first = run_import(app, tmp_path)
    second = run_import(app, tmp_path)
    assert first.exit_code == 0, first.output
    assert "2 valid of 2 shown by GAF (complete); 2 new, 0 updated, 0 invalid" in first.output
    assert "2 new" not in second.output and "0 new, 2 updated" in second.output
    assert sql(engine, "SELECT count(*) FROM prospects WHERE gaf_source_id IN ('TEST-IMP1','TEST-IMP2')")[0][0] == 2


def test_reimport_updates_facts_and_keeps_lead_and_status(app, client, engine, tmp_path):
    f = tmp_path / "gaf_residential_t.json"
    f.write_text(json.dumps(snapshot("residential", [rec("IMP3", phone="(212) 555-0131", distance_mi=40.0)])))
    run_import(app, f.parent)
    pid = sql(engine, "SELECT id FROM prospects WHERE gaf_source_id = 'TEST-IMP3'")[0][0]
    lead_id = client.post(f"/api/v1/prospects/{pid}/save").get_json()["lead"]["id"]
    client.patch(f"/api/v1/leads/{lead_id}/status", json={"status": "qualified"})
    changed_at = sql(engine, "SELECT status_changed_at FROM leads WHERE id = :i", i=lead_id)[0][0]

    f.write_text(json.dumps(snapshot("residential", [rec("IMP3", phone="(212) 555-0131", distance_mi=4.0, website_url="https://example.com/new")])))
    r = run_import(app, f.parent)
    assert "0 new, 1 updated" in r.output
    detail = client.get(f"/api/v1/prospects/{pid}").get_json()
    assert detail["distance_mi"] == 4.0 and detail["website_url"] == "https://example.com/new"
    assert detail["score"] == 35 + 10 + 10 + 10 + 5   # rescored after the update
    assert detail["lead"]["id"] == lead_id and detail["lead"]["status"] == "qualified"
    assert sql(engine, "SELECT status_changed_at FROM leads WHERE id = :i", i=lead_id)[0][0] == changed_at


def test_invalid_records_are_reported_and_valid_records_import(app, engine, tmp_path):
    records = [
        rec("IMP4"),
        rec("IMP5", profile_url="https://evil.example.com/x"),   # not a gaf.com URL
        {**rec("IMP6"), "name": ""},                             # empty name
        {**rec("IMP7"), "retrieved_at": "not a date"},
    ]
    (tmp_path / "gaf_residential_t.json").write_text(json.dumps(snapshot("residential", records, expected=4)))
    r = run_import(app, tmp_path)
    assert r.exit_code == 0, r.output
    assert "1 valid of 4 shown by GAF (partial); 1 new, 0 updated, 3 invalid" in r.output
    for sid in ("TEST-IMP5", "TEST-IMP6", "TEST-IMP7"):
        assert sid in r.output
    rows = sql(engine, "SELECT gaf_source_id FROM prospects WHERE gaf_source_id IN ('TEST-IMP4','TEST-IMP5','TEST-IMP6','TEST-IMP7')")
    assert [x[0] for x in rows] == ["TEST-IMP4"]


def test_import_scores_only_imported_rows(app, engine, tmp_path):
    before = sql(engine, "SELECT max(scored_at) FROM prospect_scores ps JOIN prospects p ON p.id = ps.prospect_id WHERE p.gaf_source_id NOT LIKE 'TEST-%'")[0][0]
    (tmp_path / "gaf_residential_t.json").write_text(json.dumps(snapshot("residential", [rec("IMP8")])))
    run_import(app, tmp_path)
    after = sql(engine, "SELECT max(scored_at) FROM prospect_scores ps JOIN prospects p ON p.id = ps.prospect_id WHERE p.gaf_source_id NOT LIKE 'TEST-%'")[0][0]
    assert before == after   # real prospects were not touched
