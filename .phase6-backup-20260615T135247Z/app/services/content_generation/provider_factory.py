"""Factory for controlled Content Factory generation providers."""
from __future__ import annotations

import os
from dataclasses import dataclass

from app.services.content_generation.providers.base import ContentGenerationProvider
from app.services.content_generation.providers.deterministic import DeterministicContentGenerationProvider
from app.services.content_generation.providers.llm import LLMContentGenerationProvider


@dataclass(frozen=True)
class GenerationSettings:
    enabled: bool
    provider: str
    max_artifacts_per_task: int
    max_scope_run_artifacts: int


def get_generation_settings() -> GenerationSettings:
    return GenerationSettings(
        enabled=os.environ.get("CONTENT_FACTORY_GENERATION_ENABLED", "false").lower() in {"1", "true", "yes"},
        provider=os.environ.get("CONTENT_FACTORY_PROVIDER", "deterministic").lower(),
        max_artifacts_per_task=int(os.environ.get("CONTENT_FACTORY_MAX_ARTIFACTS_PER_TASK", "10")),
        max_scope_run_artifacts=int(os.environ.get("CONTENT_FACTORY_MAX_SCOPE_RUN_ARTIFACTS", "250")),
    )


def get_content_generation_provider(settings: GenerationSettings | None = None) -> ContentGenerationProvider:
    settings = settings or get_generation_settings()
    if settings.provider == "deterministic":
        return DeterministicContentGenerationProvider()
    if settings.provider == "llm":
        if not settings.enabled:
            raise RuntimeError("CONTENT_FACTORY_GENERATION_ENABLED must be true before using the LLM provider.")
        return LLMContentGenerationProvider()
    if settings.provider == "disabled":
        raise RuntimeError("Content generation provider is disabled.")
    raise ValueError(f"Unsupported content generation provider: {settings.provider}")
