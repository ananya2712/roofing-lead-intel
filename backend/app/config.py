"""Configuration from environment variables. Secrets never have defaults."""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Settings read from environment variables."""
    database_url: str
    snapshot_dir: str


def sqlalchemy_url(url: str) -> str:
    """Use the psycopg 3 driver. Hosts such as Render give postgres:// or postgresql:// URLs (decision D27)."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url.removeprefix(prefix)
    return url


def load_config() -> Config:
    """Read DATABASE_URL (required) and SNAPSHOT_DIR from the environment."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set.")
    return Config(
        database_url=sqlalchemy_url(database_url),
        snapshot_dir=os.environ.get("SNAPSHOT_DIR", "/data/snapshot"),
    )
