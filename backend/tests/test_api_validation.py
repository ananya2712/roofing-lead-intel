"""API validation, error shape, 404s, and response shapes against openapi.yaml."""
import pytest

from conftest import check_schema, response_schema, sql

GETS = [
    ("/api/v1/health", "/health"),
    ("/api/v1/overview", "/overview"),
    ("/api/v1/overview?directory=commercial", "/overview"),
    ("/api/v1/prospects?page_size=100", "/prospects"),
    ("/api/v1/prospects?tier=high&directory=residential&max_distance=25&sort=distance", "/prospects"),
    ("/api/v1/prospects/stats", "/prospects/stats"),
    ("/api/v1/leads?scope=all", "/leads"),
    ("/api/v1/leads?queue=follow_up_due&sort=oldest_status_change", "/leads"),
]


@pytest.mark.parametrize("url,path", GETS)
def test_valid_get_requests_match_contract(client, test_prospects, url, path):
    r = client.get(url)
    assert r.status_code == 200
    assert check_schema(r.get_json(), response_schema(path, "get", 200)) == []


def test_detail_and_mutations_match_contract(client, test_prospects):
    pid = test_prospects["SAVE4"]
    d = client.get(f"/api/v1/prospects/{pid}")
    assert check_schema(d.get_json(), response_schema("/prospects/{prospect_id}", "get", 200)) == []
    s = client.post(f"/api/v1/prospects/{pid}/save")
    assert s.status_code == 201
    assert check_schema(s.get_json(), response_schema("/prospects/{prospect_id}/save", "post", 201)) == []
    p = client.patch(f"/api/v1/leads/{s.get_json()['lead']['id']}/status", json={"status": "qualified"})
    assert check_schema(p.get_json(), response_schema("/leads/{lead_id}/status", "patch", 200)) == []


BAD = [
    "/api/v1/prospects?tier=urgent", "/api/v1/prospects?max_distance=30", "/api/v1/prospects?page=0",
    "/api/v1/prospects?page_size=101", "/api/v1/prospects?sort=rating", "/api/v1/prospects?directory=industrial",
    "/api/v1/leads?scope=archived", "/api/v1/leads?status=dismissed", "/api/v1/leads?queue=today",
    "/api/v1/leads?sort=name", "/api/v1/leads?page=0", "/api/v1/overview?directory=x", "/api/v1/prospects/stats?directory=x",
]


@pytest.mark.parametrize("url", BAD)
def test_invalid_query_returns_422_error_shape(client, url):
    r = client.get(url)
    assert r.status_code == 422
    body = r.get_json()
    assert check_schema(body, {"$ref": "#/components/schemas/Error"}) == []
    assert body["error"]["code"] == "validation_error" and body["error"]["details"]["fields"]


def test_empty_query_values_mean_no_filter(client):
    a = client.get("/api/v1/prospects?directory=&tier=&q=").get_json()
    b = client.get("/api/v1/prospects").get_json()
    assert a["total"] == b["total"]


@pytest.mark.parametrize("body,ctype", [
    ('{"status": "won"}', "application/json"),
    ('{"status": ', "application/json"),
    ("status=contacted", "application/x-www-form-urlencoded"),
    ("[]", "application/json"),
])
def test_invalid_status_bodies_return_422_and_change_nothing(client, engine, test_prospects, body, ctype):
    lead_id = client.post(f"/api/v1/prospects/{test_prospects['SAVE5']}/save").get_json()["lead"]["id"]
    before = sql(engine, "SELECT status, status_changed_at FROM leads WHERE id = :i", i=lead_id)
    r = client.patch(f"/api/v1/leads/{lead_id}/status", data=body, content_type=ctype)
    assert r.status_code == 422
    assert r.get_json()["error"]["code"] == "validation_error"
    assert sql(engine, "SELECT status, status_changed_at FROM leads WHERE id = :i", i=lead_id) == before


@pytest.mark.parametrize("method,url", [
    ("get", "/api/v1/prospects/999999999"), ("post", "/api/v1/prospects/999999999/save"),
    ("patch", "/api/v1/leads/999999999/status"),
])
def test_missing_ids_return_404(client, method, url):
    r = getattr(client, method)(url, json={"status": "new"} if method == "patch" else None)
    assert r.status_code == 404
    assert r.get_json()["error"]["code"] == "not_found"


def test_unknown_route_uses_error_shape(client):
    r = client.get("/api/v1/nothing-here")
    assert r.status_code == 404 and "error" in r.get_json()
