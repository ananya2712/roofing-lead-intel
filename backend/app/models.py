"""Database tables.

Three tables, one for each kind of data (decision D4):

- ``prospects``: GAF source facts. One row for each GAF directory listing.
- ``prospect_scores``: the calculated priority score for a prospect (derived data).
- ``leads``: representative work. One row for each saved prospect.

Each prospect has at most one score and at most one lead. Tables are created by
``create_all()`` at startup (no migrations in the MVP, decision D5).
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

DIRECTORIES = ("residential", "commercial")
LEAD_STATUSES = ("new", "contacted", "qualified", "dismissed")


class Base(DeclarativeBase):
    """Declarative base for all tables."""


class Prospect(Base):
    """One GAF directory listing.

    GAF is the source of truth for every column. A new import updates these
    columns in place (upsert on ``directory`` + ``gaf_source_id``) and never
    touches the lead. A missing value is stored as NULL and shown as "Unknown".
    """

    __tablename__ = "prospects"
    __table_args__ = (
        # The same GAF listing can be imported again without a duplicate row.
        UniqueConstraint("directory", "gaf_source_id", name="uq_prospect_listing"),
        CheckConstraint(f"directory IN {DIRECTORIES}", name="ck_prospect_directory"),
        # Phone lookup. Since D26 the company match uses gaf_source_id, not the phone.
        Index("ix_prospects_phone_digits", "phone_digits"),
    )

    # Internal primary key.
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # GAF directory of the listing: "residential" or "commercial".
    directory: Mapped[str] = mapped_column(String(16), nullable=False)
    # GAF contractor ID from the profile URL. Unique together with directory.
    # GAF uses the same ID for a company in both directories, so it is also the company key (D26).
    gaf_source_id: Mapped[str] = mapped_column(String(32), nullable=False)
    # Link to the GAF profile page; the evidence for every fact in this row.
    profile_url: Mapped[str] = mapped_column(Text, nullable=False)
    # Company name as GAF shows it.
    name: Mapped[str] = mapped_column(Text, nullable=False)
    # Phone number as GAF shows it, for example "(201) 982-2718".
    phone: Mapped[str | None] = mapped_column(String(32))
    # Phone as 10 digits, or NULL. Not used for company matching (D26).
    phone_digits: Mapped[str | None] = mapped_column(String(16))
    # Company website from the GAF "Visit Website" link. NULL when GAF has none.
    website_url: Mapped[str | None] = mapped_column(Text)
    # Full address "street, city, state ZIP". NULL when the street is missing.
    address: Mapped[str | None] = mapped_column(Text)
    # City, used for search and display.
    city: Mapped[str | None] = mapped_column(Text)
    # Two-letter state code (NY, NJ, CT), used for the state filter.
    state: Mapped[str | None] = mapped_column(String(8))
    # "About us" text written by the contractor. Shown, not scored.
    about_text: Mapped[str | None] = mapped_column(Text)
    # GAF text such as "In business since 1995". Shown, not scored (sources can conflict).
    years_in_business: Mapped[str | None] = mapped_column(Text)
    # Miles from ZIP 10013, as GAF calculated it. Drives the distance score.
    distance_mi: Mapped[Decimal | None] = mapped_column(Numeric(6, 1))
    # Star rating 0.0–5.0 from the GAF profile. Shown, not scored. 0 is a real value; NULL is unknown.
    rating: Mapped[Decimal | None] = mapped_column(Numeric(2, 1))
    # Number of reviews on the GAF profile. Shown, not scored.
    review_count: Mapped[int | None] = mapped_column(Integer)
    # GAF distinctions, e.g. "GAF Master Elite® - Certification". Drive the certification score.
    distinctions: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default="{}")
    # Residential specialties (FORTIFIED, metal, solar) or commercial technologies (single-ply...).
    specialties: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default="{}")
    # When the GAF profile was read. Drives the 30-day freshness rule.
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # When this row was first inserted.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # When an import last changed this row.
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    score: Mapped["ProspectScore | None"] = relationship(back_populates="prospect", uselist=False)
    lead: Mapped["Lead | None"] = relationship(back_populates="prospect", uselist=False)


class ProspectScore(Base):
    """The priority score of one prospect (see ``scoring.py``).

    Derived from the prospect row only, so it can be recalculated at any time
    with ``flask rescore``. Saving a lead or changing its status never changes it.
    """

    __tablename__ = "prospect_scores"
    __table_args__ = (
        CheckConstraint("score BETWEEN 0 AND 100", name="ck_score_range"),
        # Supports the default "highest score first" order.
        Index("ix_prospect_scores_order", text("score DESC")),
    )

    # Primary key and foreign key: one score for each prospect.
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id", ondelete="CASCADE"), primary_key=True)
    # Total points, 0–100. Tier: High >= 70, Medium 45–69, Low < 45.
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    # Eight items, one for each scoring category: key, label, points, max, reason, unknown.
    breakdown: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
    # Version of the scoring rules that made this score, e.g. "v1".
    rule_version: Mapped[str] = mapped_column(String(16), nullable=False)
    # Effective time used for the freshness rule.
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    prospect: Mapped[Prospect] = relationship(back_populates="score")


class Lead(Base):
    """A prospect that a representative saved. Holds representative work only."""

    __tablename__ = "leads"
    __table_args__ = (
        CheckConstraint(f"status IN {LEAD_STATUSES}", name="ck_lead_status"),
        # One saved lead for each company (D8, D26). NULL keys do not conflict.
        Index("uq_leads_company_key", "company_key", unique=True, postgresql_where=text("company_key IS NOT NULL")),
    )

    # Internal primary key.
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # The saved prospect. Unique, so a prospect can be saved only once.
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id", ondelete="RESTRICT"), unique=True, nullable=False)
    # Copy of the prospect's gaf_source_id. Blocks a second lead for the same company
    # through its listing in the other directory (D26).
    company_key: Mapped[str | None] = mapped_column(String(32))
    # When the representative saved the prospect.
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    # Current status: new, contacted, qualified or dismissed. Starts as "new".
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="new")
    # Changes only when the status really changes. Drives the 14-day follow-up rule.
    status_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    # When any column of this row last changed.
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    prospect: Mapped[Prospect] = relationship(back_populates="lead")
