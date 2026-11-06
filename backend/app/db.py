"""Engine and session handling. One session for each request."""
from contextlib import contextmanager

from flask import g
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from .models import Base

_engine = None
_factory: sessionmaker | None = None


def init_db(database_url: str) -> None:
    """Create the engine and session factory, then create missing tables under a lock."""
    global _engine, _factory
    # A small pool: each gunicorn worker keeps at most 5 + 5 connections.
    _engine = create_engine(database_url, pool_size=5, max_overflow=5, pool_pre_ping=True)
    _factory = sessionmaker(bind=_engine, expire_on_commit=False)
    # Several gunicorn workers start at the same time. The lock lets one worker create the tables.
    with _engine.begin() as conn:
        conn.execute(text("SELECT pg_advisory_xact_lock(724001)"))
        Base.metadata.create_all(conn)


def get_session() -> Session:
    """Return the database session of this request. Create it on first use."""
    if "db" not in g:
        g.db = _factory()
    return g.db


def close_session(_exc=None) -> None:
    """Close the session at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


@contextmanager
def session_scope():
    """Session for work outside a request, for example CLI commands."""
    session = _factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
