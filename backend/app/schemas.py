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
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if v != ""}
        return data


class ProspectQuery(QueryModel):
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
        if v is not None and v not in (10, 25, 50):
            raise ValueError("max_distance must be 10, 25 or 50")
        return v
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)


class LeadQuery(QueryModel):
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
    directory: Directory | None = None


class StatusUpdate(BaseModel):
    status: LeadStatus


# ---------- responses ----------

class ScoreItem(BaseModel):
    key: str
    label: str
    points: int
    max: int
    reason: str
    unknown: bool


class LinkedListing(BaseModel):
    prospect_id: int
    directory: Directory


class ProspectSummary(BaseModel):
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
    total: int
    page: int
    page_size: int


class ProspectList(Page_):
    items: list[ProspectSummary]


class LeadInfo(BaseModel):
    id: int
    status: LeadStatus
    saved_at: datetime
    status_changed_at: datetime


class ProspectDetail(BaseModel):
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
    items: list[LeadSummary]
    status_counts: dict[str, int]
    queue_counts: dict[str, int]
    total_saved: int


class ProspectStats(BaseModel):
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
