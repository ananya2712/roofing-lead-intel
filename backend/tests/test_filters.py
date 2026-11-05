"""Filters, sorting and pagination on the real snapshot data (read only)."""
import pytest

from conftest import sql

TIER = {"high": (70, 100), "medium": (45, 69), "low": (0, 44)}


def all_pages(client, query, page_size=25):
    items, page = [], 1
    while True:
        body = client.get(f"/api/v1/prospects?{query}&page={page}&page_size={page_size}").get_json()
        items += body["items"]
        if page * page_size >= body["total"]:
            return items, body["total"]
        page += 1


COMBOS = [
    "directory=residential&tier=high&max_distance=25",
    "directory=commercial&state=NJ",
    "tier=medium&max_distance=10&sort=distance",
    "q=roof&directory=residential",
    "state=NY&tier=high&sort=name",
]


@pytest.mark.parametrize("query", COMBOS)
def test_every_result_matches_the_filters_and_pages_do_not_repeat(client, query):
    items, total = all_pages(client, query)
    params = dict(p.split("=") for p in query.split("&"))
    assert len(items) == total
    assert len({i["id"] for i in items}) == total               # no repeats across pages
    for i in items:
        if "directory" in params:
            assert i["directory"] == params["directory"]
        if "tier" in params:
            lo, hi = TIER[params["tier"]]
            assert lo <= i["score"] <= hi and i["tier"] == params["tier"]
        if "max_distance" in params:
            assert i["distance_mi"] is not None and i["distance_mi"] <= float(params["max_distance"])
        if "state" in params:
            assert i["state"] == params["state"]
        if "q" in params:
            assert params["q"] in i["name"].lower() or params["q"] in (i["city"] or "").lower()


def test_total_matches_database_count(client, engine):
    body = client.get("/api/v1/prospects?directory=commercial&state=NJ").get_json()
    n = sql(engine, "SELECT count(*) FROM prospects WHERE directory='commercial' AND state='NJ'")[0][0]
    assert body["total"] == n


def test_default_order_is_score_then_distance_then_name_and_stable(client):
    items, _ = all_pages(client, "directory=residential", page_size=50)
    keys = [(-i["score"], i["distance_mi"] if i["distance_mi"] is not None else 1e9, i["name"]) for i in items]
    assert keys == sorted(keys)
    again, _ = all_pages(client, "directory=residential", page_size=50)
    assert [i["id"] for i in items] == [i["id"] for i in again]


def test_distance_and_name_sorts(client):
    dist, _ = all_pages(client, "sort=distance&directory=commercial", page_size=100)
    d = [i["distance_mi"] for i in dist]
    assert d == sorted(d)
    names, _ = all_pages(client, "sort=name&state=CT", page_size=100)
    n = [i["name"] for i in names]
    assert n == sorted(n)


def test_page_beyond_the_end_is_empty_not_an_error(client):
    body = client.get("/api/v1/prospects?page=999").get_json()
    assert body["items"] == [] and body["total"] > 0


def test_cert_tier_filter_uses_the_breakdown(client):
    items, _ = all_pages(client, "cert_tier=certified&directory=commercial", page_size=100)
    assert items
    for i in items[:10]:
        bd = client.get(f"/api/v1/prospects/{i['id']}").get_json()["score_breakdown"]
        assert next(b for b in bd if b["key"] == "certification")["points"] == 12


def test_hide_saved_excludes_saved_prospects_and_their_twins(client, test_prospects):
    client.post(f"/api/v1/prospects/{test_prospects['TWINR']}/save")
    items, _ = all_pages(client, "q=zztest&hide_saved=true", page_size=100)
    ids = {i["id"] for i in items}
    assert test_prospects["TWINR"] not in ids and test_prospects["TWINC"] not in ids
