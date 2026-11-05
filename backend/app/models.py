"""Database tables.

The tables follow the field groups that the design review approved:
GAF source data, deterministic score, and representative work.
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
    pass


class Prospect(Base):
    """One GAF directory listing. GAF is the source of truth for every column."""

    __tablename__ = "prospects"
    __table_args__ = (
        UniqueConstraint("directory", "gaf_source_id", name="uq_prospect_listing"),
        CheckConstraint(f"directory IN {DIRECTORIES}", name="ck_prospect_directory"),
        Index("ix_prospects_phone_digits", "phone_digits"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    directory: Mapped[str] = mapped_column(String(16), nullable=False)
    gaf_source_id: Mapped[str] = mapped_column(String(32), nullable=False)
    profile_url: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32))
    # Digits only. Links the same company across the two directories.
    phone_digits: Mapped[str | None] = mapped_column(String(16))
    website_url: Mapped[str | None] = mapped_column(Text)
    address: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(Text)
    state: Mapped[str | None] = mapped_column(String(8))
    about_text: Mapped[str | None] = mapped_column(Text)
    years_in_business: Mapped[str | None] = mapped_column(Text)
    distance_mi: Mapped[Decimal | None] = mapped_column(Numeric(6, 1))
    rating: Mapped[Decimal | None] = mapped_column(Numeric(2, 1))
    review_count: Mapped[int | None] = mapped_column(Integer)
    distinctions: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default="{}")
    specialties: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default="{}")
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    score: Mapped["ProspectScore | None"] = relationship(back_populates="prospect", uselist=False)
    lead: Mapped["Lead | None"] = relationship(back_populates="prospect", uselist=False)


class ProspectScore(Base):
    """Deterministic score. Derived from the prospect row only."""

    __tablename__ = "prospect_scores"
    __table_args__ = (
        CheckConstraint("score BETWEEN 0 AND 100", name="ck_score_range"),
        Index("ix_prospect_scores_order", text("score DESC")),
    )

    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id", ondelete="CASCADE"), primary_key=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    breakdown: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
    rule_version: Mapped[str] = mapped_column(String(16), nullable=False)
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    prospect: Mapped[Prospect] = relationship(back_populates="score")


class Lead(Base):
    """A prospect that a representative saved. Holds representative work only."""

    __tablename__ = "leads"
    __table_args__ = (
        CheckConstraint(f"status IN {LEAD_STATUSES}", name="ck_lead_status"),
        # One saved lead for each company (D8). NULL keys do not conflict.
        Index("uq_leads_company_key", "company_key", unique=True, postgresql_where=text("company_key IS NOT NULL")),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id", ondelete="RESTRICT"), unique=True, nullable=False)
    company_key: Mapped[str | None] = mapped_column(String(16))
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="new")
    status_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    prospect: Mapped[Prospect] = relationship(back_populates="lead")

