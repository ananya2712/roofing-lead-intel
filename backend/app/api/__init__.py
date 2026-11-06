"""REST routes under /api/v1. Handlers validate input and call services only."""
from flask import Blueprint, jsonify, request
from sqlalchemy import text

from .. import services
from ..db import get_session
from ..schemas import DirectoryQuery, LeadQuery, ProspectQuery, StatusUpdate

api_bp = Blueprint("api", __name__)


def _json(model, status=200):
    """Return a Pydantic response model as JSON with the given HTTP status."""
    return jsonify(model.model_dump(mode="json")), status


def _body() -> dict:
    """Return the JSON body as a dict. Any other body becomes {}, so validation names the missing fields."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


@api_bp.get("/health")
def health():
    """GET /health: check that the API can reach the database."""
    get_session().execute(text("SELECT 1"))
    return jsonify({"status": "ok"})


@api_bp.get("/overview")
def overview():
    """GET /overview: Sales dashboard counts and call lists, optionally for one directory."""
    q = DirectoryQuery.model_validate(request.args.to_dict())
    return _json(services.overview(get_session(), q.directory))


@api_bp.get("/prospects")
def list_prospects():
    """GET /prospects: one page of prospects after search, filters and sort."""
    q = ProspectQuery.model_validate(request.args.to_dict())
    return _json(services.list_prospects(get_session(), q))


@api_bp.get("/prospects/stats")
def prospect_stats():
    """GET /prospects/stats: counts for the Prospects KPI cards and charts."""
    q = DirectoryQuery.model_validate(request.args.to_dict())
    return _json(services.prospect_stats(get_session(), q.directory))


@api_bp.get("/prospects/<int:prospect_id>")
def get_prospect(prospect_id: int):
    """GET /prospects/{id}: source facts, score breakdown, unknown fields and lead state."""
    return _json(services.prospect_detail(get_session(), prospect_id))


@api_bp.post("/prospects/<int:prospect_id>/save")
def save_prospect(prospect_id: int):
    """POST /prospects/{id}/save: save as a lead. 201 for a new lead, 200 when it exists."""
    detail, created = services.save_prospect(get_session(), prospect_id)
    return _json(detail, 201 if created else 200)


@api_bp.get("/leads")
def list_leads():
    """GET /leads: saved leads with call-list filters, counts, sort and pages."""
    q = LeadQuery.model_validate(request.args.to_dict())
    return _json(services.list_leads(get_session(), q))


@api_bp.post("/leads/<int:lead_id>/status")
def update_status(lead_id: int):
    """POST /leads/{id}/status: change the status of a lead."""
    body = StatusUpdate.model_validate(_body())
    return _json(services.update_status(get_session(), lead_id, body.status))

