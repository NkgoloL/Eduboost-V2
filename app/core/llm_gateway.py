"""Compatibility helpers for legacy lesson-service LLM gateway imports."""

from app.core.config import settings
from app.services.executive import ExecutiveService


def active_provider_label() -> str:
    if settings.LLM_PROVIDER != "auto":
        return settings.LLM_PROVIDER
    if settings.GOOGLE_API_KEY:
        return "google"
    if settings.GROQ_API_KEY:
        return "groq"
    if settings.ANTHROPIC_API_KEY:
        return "anthropic"
    return "fallback"

__all__ = ["ExecutiveService", "active_provider_label"]
