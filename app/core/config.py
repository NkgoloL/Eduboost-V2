"""EduBoost V2 core configuration.

This module establishes the V2 baseline settings surface described in the
master execution manifest while remaining compatible with the current app.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class V2Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="EduBoost V2", alias="APP_NAME")
    app_env: Literal["development", "test", "staging", "production"] = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    jwt_secret: str = Field(default="", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")

    constitutional_ai_enabled: bool = True
    append_only_audit_table: str = "audit_log_entries"


@lru_cache
def get_v2_settings() -> V2Settings:
    return V2Settings()
