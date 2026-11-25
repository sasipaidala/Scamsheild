"""Typed configuration for ScamShield AI."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    environment: str
    database_path: Path
    log_level: str
    app_name: str = "ScamShield AI"
    app_version: str = "0.3.0"

    @classmethod
    def from_env(cls) -> "Settings":
        """Load and validate settings; relative paths resolve from project root."""
        load_dotenv(PROJECT_ROOT / ".env", override=False)

        environment = os.getenv("SCAMSHIELD_ENV", "development").strip().lower()
        if environment not in {"development", "test", "production"}:
            raise ValueError(
                "SCAMSHIELD_ENV must be development, test, or production."
            )

        raw_database_path = os.getenv(
            "SCAMSHIELD_DATABASE_PATH", "data/scamshield.db"
        ).strip()
        if not raw_database_path:
            raise ValueError("SCAMSHIELD_DATABASE_PATH cannot be empty.")

        database_path = Path(raw_database_path).expanduser()
        if not database_path.is_absolute() and str(database_path) != ":memory:":
            database_path = (PROJECT_ROOT / database_path).resolve()

        log_level = os.getenv("SCAMSHIELD_LOG_LEVEL", "INFO").strip().upper()
        if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("SCAMSHIELD_LOG_LEVEL is not a supported log level.")

        return cls(
            environment=environment,
            database_path=database_path,
            log_level=log_level,
        )
