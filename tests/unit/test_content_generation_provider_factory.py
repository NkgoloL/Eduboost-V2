from __future__ import annotations

import pytest

from app.services.content_generation.provider_factory import GenerationSettings, get_content_generation_provider
from app.services.content_generation.providers.deterministic import DeterministicContentGenerationProvider


def test_deterministic_provider_factory_returns_safe_provider() -> None:
    provider = get_content_generation_provider(GenerationSettings(True, "deterministic", 10, 250))

    assert isinstance(provider, DeterministicContentGenerationProvider)


def test_llm_provider_requires_generation_enabled() -> None:
    with pytest.raises(RuntimeError, match="GENERATION_ENABLED"):
        get_content_generation_provider(GenerationSettings(False, "llm", 10, 250))


def test_disabled_provider_fails_closed() -> None:
    with pytest.raises(RuntimeError, match="disabled"):
        get_content_generation_provider(GenerationSettings(False, "disabled", 10, 250))
