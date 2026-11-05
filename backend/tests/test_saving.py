"""Saving and duplicates, including parallel requests against the running API."""
from concurrent.futures import ThreadPoolExecutor

import requests

from conftest import LIVE_API, sql


def lead_count(engine, pid):
    return sql(engine, "SELECT count(*) FROM leads WHERE prospect_id = :p", p=pid)[0][0]


def test_first_save_creates_one_lead_with_status_new(client, engine, test_prospects):
    pid = test_prospects["SAVE2"]
    r = client.post(f"/api/v1/prospects/{pid}/save")
    assert r.status_code == 201
    assert r.get_json()["lead"]["status"] == "new"
    assert lead_count(engine, pid) == 1


def test_repeated_save_returns_200_and_no_duplicate(client, engine, test_prospects):
    pid = test_prospects["SAVE2"]
    first = client.post(f"/api/v1/prospects/{pid}/save").get_json()["lead"]["id"]
    again = client.post(f"/api/v1/prospects/{pid}/save")
    assert again.status_code == 200
    assert again.get_json()["lead"]["id"] == first
    assert lead_count(engine, pid) == 1


def test_parallel_saves_of_same_prospect_create_one_lead(engine, test_prospects):
    pid = test_prospects["SAVE3"]
    with ThreadPoolExecutor(max_workers=8) as pool:
        codes = list(pool.map(lambda _: requests.post(f"{LIVE_API}/prospects/{pid}/save", timeout=15).status_code, range(8)))
    assert codes.count(201) == 1, codes
    assert set(codes) <= {200, 201}, codes
    assert lead_count(engine, pid) == 1


def test_same_company_in_both_directories_returns_409_with_existing_lead(client, engine, test_prospects):
    r_id, c_id = test_prospects["TWINR"], test_prospects["TWINC"]
    assert client.post(f"/api/v1/prospects/{r_id}/save").status_code == 201
    r = client.post(f"/api/v1/prospects/{c_id}/save")
    assert r.status_code == 409
    err = r.get_json()["error"]
    assert err["code"] == "company_already_saved"
    assert err["details"] == {"prospect_id": r_id, "directory": "residential"}
    assert lead_count(engine, c_id) == 0
    detail = client.get(f"/api/v1/prospects/{c_id}").get_json()
    assert detail["saved_via"] == {"prospect_id": r_id, "directory": "residential"}
    assert detail["also_listed_in"]["prospect_id"] == r_id


def test_parallel_saves_of_both_listings_create_one_lead(engine, test_prospects):
    ids = [test_prospects["TWINR"], test_prospects["TWINC"]] * 4
    with ThreadPoolExecutor(max_workers=8) as pool:
        codes = list(pool.map(lambda pid: requests.post(f"{LIVE_API}/prospects/{pid}/save", timeout=15).status_code, ids))
    total = sql(engine, "SELECT count(*) FROM leads WHERE prospect_id IN (:a, :b)", a=ids[0], b=ids[1])[0][0]
    assert total == 1, codes
    assert codes.count(201) == 1 and set(codes) <= {200, 201, 409}, codes
