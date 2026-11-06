"""Pydantic request and response schemas. openapi.yaml mirrors these models."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

Directory = Literal["residential", "commercial"]
Tier = Literal["high", "medium", "low"]
LeadStatus = Literal["new", "contacted", "qualified", "dismissed"]
CertTier = Literal["top", "certified", "none"]


# ---------- requests ----------

class QueryModel(BaseModel):
    """Base for query strings: an empty value such as ?directory= means "no filter"."""

    @model_validator(mode="before")
    @classmethod
    def _drop_empty(cls, data):
        """Treat an empty query value (?tier=) as no filter."""
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if v != ""}
        return data


class ProspectQuery(QueryModel):
    """Query parameters for GET /prospects."""
    q: str | None = Field(default=None, max_length=100)
    directory: Directory | None = None
    tier: Tier | None = None
    # Query strings arrive as text ("25"). Literal[10, 25, 50] does not convert text, so
    # the value is an int checked against the allowed bands.
    max_distance: int | None = None
    state: str | None = Field(default=None, max_length=4)
    cert_tier: CertTier | None = None
    hide_saved: bool = False
    sort: Literal["score", "distance", "name"] = "score"

    @field_validator("max_distance")
    @classmethod
    def _band(cls, v: int | None) -> int | None:
        """Allow only the distance bands 10, 25 and 50 miles."""
        if v is not None and v not in (10, 25, 50):
            raise ValueError("max_distance must be 10, 25 or 50")
        return v
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)


class LeadQuery(QueryModel):
    """Query parameters for GET /leads."""
    q: str | None = Field(default=None, max_length=100)
    # scope replaces the old status=dismissed / show_dismissed overlap.
    scope: Literal["active", "all", "dismissed"] = "active"
    status: Literal["new", "contacted", "qualified"] | None = None
    queue: Literal["first_contact", "follow_up_due"] | None = None
    directory: Directory | None = None
    tier: Tier | None = None
    sort: Literal["priority", "recently_saved", "oldest_status_change"] = "priority"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)


class DirectoryQuery(QueryModel):
    """Optional directory filter for the dashboard and the stats."""
    directory: Directory | None = None


class StatusUpdate(BaseModel):
    """Request body for POST /leads/{id}/status."""
    status: LeadStatus


# ---------- responses ----------

class ScoreItem(BaseModel):
    """One scoring category in a score breakdown."""
    key: str
    label: str
    points: int
    max: int
    reason: str
    unknown: bool


class LinkedListing(BaseModel):
    """A link to another listing of the same company."""
    prospect_id: int
    directory: Directory


class ProspectSummary(BaseModel):
    """One row of the Prospects table."""
    id: int
    directory: Directory
    name: str
    city: str | None
    state: str | None
    phone: str | None
    distance_mi: float | None
    rating: float | None
    review_count: int | None
    score: int
    tier: Tier
    top_reason: str
    has_website: bool
    saved_lead_id: int | None
    also_listed_in: LinkedListing | None
    saved_via: LinkedListing | None


class Page_(BaseModel):
    """Paging fields shared by list responses."""
    total: int
    page: int
    page_size: int


class ProspectList(Page_):
    """One page of Prospects table rows."""
    items: list[ProspectSummary]


class LeadInfo(BaseModel):
    """Lead state shown on the prospect page."""
    id: int
    status: LeadStatus
    saved_at: datetime
    status_changed_at: datetime


class ProspectDetail(BaseModel):
    """All data that the prospect page shows."""
    id: int
    directory: Directory
    gaf_source_id: str
    profile_url: str
    name: str
    phone: str | None
    website_url: str | None
    address: str | None
    city: str | None
    state: str | None
    about_text: str | None
    years_in_business: str | None
    distance_mi: float | None
    rating: float | None
    review_count: int | None
    distinctions: list[str]
    specialties: list[str]
    retrieved_at: datetime
    score: int
    tier: Tier
    score_breakdown: list[ScoreItem]
    scored_at: datetime
    unknown_fields: list[str]
    not_in_public_sources: list[str]
    also_listed_in: LinkedListing | None
    saved_via: LinkedListing | None
    lead: LeadInfo | None


class LeadSummary(BaseModel):
    """One saved-lead row, with its top reason and follow-up flag."""
    lead_id: int
    prospect_id: int
    name: str
    city: str | None
    state: str | None
    directory: Directory
    phone: str | None
    score: int
    tier: Tier
    status: LeadStatus
    status_changed_at: datetime
    saved_at: datetime
    distance_mi: float | None
    top_reason: str
    follow_up_due: bool


class LeadList(Page_):
    """One page of leads, plus counts for all saved leads in the directory."""
    items: list[LeadSummary]
    status_counts: dict[str, int]
    queue_counts: dict[str, int]
    total_saved: int


class ProspectStats(BaseModel):
    """Counts for the Prospects KPI cards and charts."""
    total: int
    high: int
    saved: int
    high_unsaved: int
    tiers: dict[str, int]
    directories: dict[str, int]
    distance_bands: dict[str, int]
    states: list[str]
    snapshot_retrieved_at: datetime | None


class Overview(BaseModel):
    """Counts and lists for the Sales dashboard."""
    saved: int
    not_contacted: int
    contacted: int
    qualified: int
    dismissed: int
    contacted_pct: int
    follow_up_days: int
    call_next: list[LeadSummary]
    follow_up: list[LeadSummary]
    top_unsaved: list[ProspectSummary]
    snapshot_retrieved_at: datetime | None
