"""Provider protocol for Content Factory generation."""
from __future__ import annotations

from typing import Protocol

from app.services.content_generation.prompt_payloads import (
    DiagnosticGenerationRequest,
    GeneratedDiagnosticItem,
    GeneratedLesson,
    LessonGenerationRequest,
)


class ContentGenerationProvider(Protocol):
    provider_name: str
    model_name: str

    async def generate_diagnostic_items(
        self,
        request: DiagnosticGenerationRequest,
    ) -> list[GeneratedDiagnosticItem]:
        ...

    async def generate_lessons(
        self,
        request: LessonGenerationRequest,
    ) -> list[GeneratedLesson]:
        ...

    async def generate_assessment_blueprints(
        self,
        request: dict,
    ) -> list[dict]:
        ...

    async def generate_study_plan_templates(
        self,
        request: dict,
    ) -> list[dict]:
        ...
