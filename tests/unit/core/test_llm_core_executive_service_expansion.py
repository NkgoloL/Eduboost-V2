"""Comprehensive unit tests for Core LLM ExecutiveService, provider labeling, and semantic caching."""
from __future__ import annotations

from pathlib import Path
import pytest

from app.core.config import settings
from app.core.llm import (
    _cache_key,
    _google_model_name,
    active_provider_label,
    _resolve_project_path,
    _local_hf_configured,
    ExecutiveService,
)


class TestLLMCoreHelpers:
    def test_cache_key_generation(self):
        k1 = _cache_key(grade=4, subject="Mathematics", topic="Fractions", language="en", archetype="visual")
        k2 = _cache_key(grade=4, subject="Mathematics", topic="Fractions", language="en", archetype="visual")
        k3 = _cache_key(grade=5, subject="Mathematics", topic="Fractions", language="en", archetype="visual")

        assert k1.startswith("lesson_cache:")
        assert k1 == k2
        assert k1 != k3

    def test_google_model_name_prefix_stripping(self, monkeypatch):
        monkeypatch.setattr(settings, "GOOGLE_MODEL", "models/gemini-1.5-flash")
        assert _google_model_name() == "gemini-1.5-flash"

        monkeypatch.setattr(settings, "GOOGLE_MODEL", "gemini-1.5-pro")
        assert _google_model_name() == "gemini-1.5-pro"

    def test_active_provider_label(self, monkeypatch):
        monkeypatch.setattr(settings, "LLM_PROVIDER", "groq")
        assert active_provider_label() == "groq"

        monkeypatch.setattr(settings, "LLM_PROVIDER", "auto")
        monkeypatch.setattr(settings, "GOOGLE_API_KEY", "test-google-key")
        assert active_provider_label() == "google"

    def test_resolve_project_path(self):
        # Absolute path stays absolute
        abs_p = Path("/tmp/absolute/model")
        assert _resolve_project_path(str(abs_p)) == abs_p

        # Relative path resolves relative to PROJECT_ROOT
        rel_p = "data/models/test"
        resolved = _resolve_project_path(rel_p)
        assert resolved.is_absolute()
        assert str(resolved).endswith(rel_p)

    def test_executive_service_init(self):
        exec_service = ExecutiveService()
        assert exec_service._judiciary is not None
        assert exec_service._caps_validator is not None
