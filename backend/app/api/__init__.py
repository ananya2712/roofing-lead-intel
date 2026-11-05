"""REST routes under /api/v1. Handlers validate input and call services only."""
from flask import Blueprint, jsonify, request
from sqlalchemy import text

from .. import services
from ..db import get_session
from ..schemas import DirectoryQuery, LeadQuery, ProspectQuery, StatusUpdate

api_bp = Blueprint("api", __name__)


def _json(model, status=200):
    return jsonify(model.model_dump(mode="json")), status


def _body() -> dict:
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


@api_bp.get("/health")
def health():
    get_session().execute(text("SELECT 1"))
    return jsonify({"status": "ok"})


@api_bp.get("/overview")
def overview():
    q = DirectoryQuery.model_validate(request.args.to_dict())
    return _json(services.overview(get_session(), q.directory))


@api_bp.get("/prospects")
def list_prospects():
    q = ProspectQuery.model_validate(request.args.to_dict())
    return _json(services.list_prospects(get_session(), q))


@api_bp.get("/prospects/stats")
def prospect_stats():
    q = DirectoryQuery.model_validate(request.args.to_dict())
    return _json(services.prospect_stats(get_session(), q.directory))


@api_bp.get("/prospects/<int:prospect_id>")
def get_prospect(prospect_id: int):
    return _json(services.prospect_detail(get_session(), prospect_id))


@api_bp.post("/prospects/<int:prospect_id>/save")
def save_prospect(prospect_id: int):
    detail, created = services.save_prospect(get_session(), prospect_id)
    return _json(detail, 201 if created else 200)


@api_bp.get("/leads")
def list_leads():
    q = LeadQuery.model_validate(request.args.to_dict())
    return _json(services.list_leads(get_session(), q))


@api_bp.post("/leads/<int:lead_id>/status")
def update_status(lead_id: int):
    body = StatusUpdate.model_validate(_body())
    return _json(services.update_status(get_session(), lead_id, body.status))

