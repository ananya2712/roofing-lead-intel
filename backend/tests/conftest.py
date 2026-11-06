"""Shared fixtures.

The user chose to run tests against the demo database (no separate test database).
Isolation rule: every test row has a gaf_source_id that starts with "TEST-" and a name
that starts with "ZZTEST". Tests create and delete only those rows. Real rows are read only.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[2]


def _env() -> dict:
    """Read KEY=VALUE pairs from the repository .env file (for the database password)."""
    values = {}
    for line in (ROOT / ".env").read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip()
    return values


ENV = _env()
DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    f"postgresql+psycopg://{ENV['POSTGRES_USER']}:{ENV['POSTGRES_PASSWORD']}@localhost:5433/{ENV['POSTGRES_DB']}",
)
LIVE_API = os.environ.get("LIVE_API", "http://localhost:5001/api/v1")
FRONTEND = os.environ.get("FRONTEND_URL", "http://localhost:3000")
NOW = datetime.now(timezone.utc)
STALE = NOW - timedelta(days=40)

CLEANUP_SQL = [
    "DELETE FROM leads WHERE prospect_id IN (SELECT id FROM prospects WHERE gaf_source_id LIKE 'TEST-%')",
    "DELETE FROM prospects WHERE gaf_source_id LIKE 'TEST-%'",
]


def rec(sid: str, **kw) -> dict:
    """A snapshot record with safe defaults. Phone numbers use the fictional 555-01xx range."""
    base = {
        "gaf_source_id": f"TEST-{sid}",
        "profile_url": f"https://www.gaf.com/en-us/roofing-contractors/residential/test/zztest-{sid.lower()}",
        "name": f"ZZTEST {sid}",
        "phone": None, "website_url": None, "street": None, "city": "Testville", "state": "NJ",
        "postal_code": "07000", "about_text": None, "years_in_business": None, "distance_mi": 30.0,
        "rating": None, "review_count": None, "distinctions": [], "specialties": [],
        "retrieved_at": NOW.isoformat(),
    }
    base.update(kw)
    return base


FULL = {"phone": "(212) 555-0101", "website_url": "https://example.com/zztest", "street": "1 Test St"}

# Expected totals are calculated by hand from the v1 table in docs/ARCHITECTURE_AND_DESIGN.md.
RESIDENTIAL = [
    # sid, fields, expected score, expected tier
    ("MAX", dict(distance_mi=5.0, distinctions=["GAF Master Elite® - Certification"], specialties=["FORTIFIED Roof™"], **FULL), 100, "high"),
    ("D10", dict(distance_mi=10.0), 35 + 10 + 5, "medium"),        # 10.0 mi is still in the <=10 band
    ("D10P", dict(distance_mi=10.1), 22 + 10 + 5, "low"),           # 37
    ("D25", dict(distance_mi=25.0), 22 + 10 + 5, "low"),
    ("D25P", dict(distance_mi=25.1), 10 + 10 + 5, "low"),
    ("D50", dict(distance_mi=50.0), 10 + 10 + 5, "low"),
    ("DNONE", dict(distance_mi=None), 0 + 10 + 5, "low"),
    ("T70", dict(distance_mi=5.0, phone="(212) 555-0102", street="2 Test St", specialties=["Metal"]), 70, "high"),
    ("T69", dict(distance_mi=20.0, distinctions=["GAF Certified™ - Certification"], phone="(212) 555-0103",
                 website_url="https://example.com/t69", street="3 Test St", retrieved_at=STALE.isoformat()), 69, "medium"),
    ("T45", dict(distance_mi=5.0, retrieved_at=STALE.isoformat()), 45, "medium"),
    ("T44", dict(distance_mi=20.0, distinctions=["GAF Certified™ - Certification"], retrieved_at=STALE.isoformat()), 44, "low"),
    ("ZERO", dict(distance_mi=12.0, rating=0.0, review_count=0, phone="(212) 555-0104"), 22 + 10 + 10 + 5, "medium"),
    # TWINR and TWINC are one company: GAF gives it the same ID in both directories (D26).
    ("TWINR", dict(gaf_source_id="TEST-TWIN", distance_mi=8.0, phone="(212) 555-0190", **{k: v for k, v in FULL.items() if k != "phone"}), 35 + 10 + 10 + 10 + 5 + 5, "high"),
    ("SAVE1", dict(distance_mi=9.0, phone="(212) 555-0111"), 35 + 10 + 10 + 5, "medium"),
    ("SAVE2", dict(distance_mi=9.0, phone="(212) 555-0112"), 60, "medium"),
    ("SAVE3", dict(distance_mi=9.0, phone="(212) 555-0113"), 60, "medium"),
    ("SAVE4", dict(distance_mi=9.0, phone="(212) 555-0114"), 60, "medium"),
    ("SAVE5", dict(distance_mi=9.0, phone="(212) 555-0115"), 60, "medium"),
    ("SAVE6", dict(distance_mi=9.0, phone="(212) 555-0116"), 60, "medium"),
    ("UI1", dict(distance_mi=9.5, phone="(212) 555-0121", distinctions=["GAF Master Elite® - Certification"]), 35 + 20 + 10 + 10 + 5, "high"),
    ("UI2", dict(distance_mi=9.5, phone="(212) 555-0122"), 60, "medium"),
    ("UI3", dict(distance_mi=9.5, phone="(212) 555-0123"), 60, "medium"),
]
COMMERCIAL = [
    ("CNOTECH", dict(distance_mi=30.0), 10 + 0 + 5, "low"),
    ("CTECH", dict(distance_mi=30.0, specialties=["Single-Ply Roofer"], distinctions=["GAF GoldElite™ Commercial Contractor"]), 10 + 12 + 10 + 5, "low"),
    ("TWINC", dict(gaf_source_id="TEST-TWIN", distance_mi=8.0, phone="(212) 555-0190", specialties=["Asphaltic Roofer"]), 35 + 10 + 10 + 5, "medium"),
]


def snapshot(directory: str, records: list[dict], expected: int | None = None) -> dict:
    """Build a snapshot file body around the given test records."""
    return {
        "source": "TEST", "directory": directory, "postal_code": "10013", "radius_mi": 50,
        "search_url": "https://example.com/test", "expected_total": expected if expected is not None else len(records),
        "collected_at": NOW.isoformat(), "collection_method": "pytest fixture", "records": records,
    }


@pytest.fixture(scope="session")
def engine():
    """Database engine for the demo database. Deletes TEST- rows before and after the run."""
    eng = create_engine(DB_URL)
    with eng.begin() as c:
        for q in CLEANUP_SQL:
            c.execute(text(q))
    yield eng
    with eng.begin() as c:
        for q in CLEANUP_SQL:
            c.execute(text(q))
    eng.dispose()


@pytest.fixture(scope="session")
def app(engine):
    """Flask app connected to the demo database."""
    from app import create_app
    from app.config import Config

    return create_app(Config(database_url=DB_URL, snapshot_dir="/nonexistent"))


@pytest.fixture()
def client(app):
    """Flask test client for in-process API calls."""
    return app.test_client()


@pytest.fixture(scope="session")
def test_prospects(app, engine, tmp_path_factory) -> dict[str, int]:
    """Import the TEST- records through the real importer and score only them."""
    from app.collection.importer import import_file, rescore_all
    from app.db import session_scope

    folder = tmp_path_factory.mktemp("snap")
    res = folder / "gaf_residential_test.json"
    com = folder / "gaf_commercial_test.json"
    res.write_text(json.dumps(snapshot("residential", [rec(s, **f) for s, f, _, _ in RESIDENTIAL])))
    com.write_text(json.dumps(snapshot("commercial", [
        rec(s, profile_url=f"https://www.gaf.com/en-us/roofing-contractors/commercial/zztest-{s.lower()}", **f)
        for s, f, _, _ in COMMERCIAL])))
    with app.app_context(), session_scope() as s:
        ids = import_file(s, res).prospect_ids + import_file(s, com).prospect_ids
        rescore_all(s, NOW, ids)
    # Map each record label to its prospect id. The twin labels share one GAF ID,
    # so the lookup uses directory + GAF ID.
    labels = {("residential", rec(s, **f)["gaf_source_id"]): s for s, f, _, _ in RESIDENTIAL}
    labels |= {("commercial", rec(s, **f)["gaf_source_id"]): s for s, f, _, _ in COMMERCIAL}
    with engine.connect() as c:
        rows = c.execute(text("SELECT directory, gaf_source_id, id FROM prospects WHERE gaf_source_id LIKE 'TEST-%'")).all()
    return {labels[(d, sid)]: pid for d, sid, pid in rows if (d, sid) in labels}


@pytest.fixture(autouse=True)
def _clean_test_leads(engine):
    """Each test starts and ends with no leads on TEST- prospects."""
    with engine.begin() as c:
        c.execute(text(CLEANUP_SQL[0]))
    yield
    with engine.begin() as c:
        c.execute(text(CLEANUP_SQL[0]))


def sql(engine, query: str, **params):
    """Run one SQL statement in its own transaction. Return rows only when it returns rows."""
    with engine.begin() as c:
        result = c.execute(text(query), params)
        return result.all() if result.returns_rows else []


# ---------- OpenAPI response check ----------

OPENAPI = yaml.safe_load((ROOT / "openapi.yaml").read_text())


def _resolve(schema: dict) -> dict:
    """Follow $ref links until a real OpenAPI schema is found."""
    while "$ref" in schema:
        schema = OPENAPI["components"]["schemas"][schema["$ref"].split("/")[-1]]
    return schema


def check_schema(value, schema: dict, path: str = "$") -> list[str]:
    """Small OpenAPI 3.0 checker: $ref, allOf, nullable, type, enum, required, properties, items."""
    errors: list[str] = []
    nullable = schema.get("nullable", False)
    if "allOf" in schema:
        if value is None and nullable:
            return []
        for sub in schema["allOf"]:
            errors += check_schema(value, sub, path)
        return errors
    schema = _resolve(schema)
    if value is None:
        return [] if nullable or schema.get("nullable") else [f"{path}: null not allowed"]
    t = schema.get("type")
    types = {"object": dict, "array": list, "string": str, "boolean": bool}
    if t == "integer" and not (isinstance(value, int) and not isinstance(value, bool)):
        errors.append(f"{path}: expected integer, got {type(value).__name__}")
    elif t == "number" and not (isinstance(value, (int, float)) and not isinstance(value, bool)):
        errors.append(f"{path}: expected number")
    elif t in types and not isinstance(value, types[t]):
        errors.append(f"{path}: expected {t}, got {type(value).__name__}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in {schema['enum']}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: missing")
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                errors += check_schema(value[key], sub, f"{path}.{key}")
        extra = set(value) - set(schema.get("properties", {}))
        if extra and schema.get("properties") and not schema.get("additionalProperties"):
            errors.append(f"{path}: fields not in the contract: {sorted(extra)}")
        if isinstance(schema.get("additionalProperties"), dict):
            for k, v in value.items():
                errors += check_schema(v, schema["additionalProperties"], f"{path}.{k}")
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errors += check_schema(item, schema["items"], f"{path}[{i}]")
    return errors


def response_schema(path: str, method: str, status: int) -> dict:
    """Return the openapi.yaml JSON schema for one path, method and status."""
    op = OPENAPI["paths"][path][method]
    resp = op["responses"][str(status)]
    if "$ref" in resp:
        resp = OPENAPI["components"]["responses"][resp["$ref"].split("/")[-1]]
    return resp["content"]["application/json"]["schema"]
