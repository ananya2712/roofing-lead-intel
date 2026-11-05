"""Configuration from environment variables. Secrets never have defaults."""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    database_url: str
    snapshot_dir: str


def load_config() -> Config:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set.")
    return Config(
        database_url=database_url,
        snapshot_dir=os.environ.get("SNAPSHOT_DIR", "/data/snapshot"),
    )
