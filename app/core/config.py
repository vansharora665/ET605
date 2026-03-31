from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "ET605 Merge System"
    app_version: str = "1.0.0"
    api_prefix: str = "/merge"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    database_url: str = ""
    recommendation_threshold: float = 0.60
    scoring_profile: str = "revised_spec"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    default_sqlite = Path.cwd() / "merge_system.db"
    return Settings(
        database_url=os.getenv(
            "DATABASE_URL",
            f"sqlite+pysqlite:///{default_sqlite}",
        ),
        recommendation_threshold=float(
            os.getenv("RECOMMENDATION_THRESHOLD", "0.60")
        ),
        scoring_profile=os.getenv("SCORING_PROFILE", "revised_spec"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
