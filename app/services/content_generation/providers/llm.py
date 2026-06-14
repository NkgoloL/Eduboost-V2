"""LLM Content Generation Provider - Integrated with Phase 1 Provider Router.

This provider delegates to the canonical ProviderRouter from app/services/llm_provider.py,
which implements the accepted Azure-primary provider strategy with Anthropic/Groq fallback.
"""
from __future__ import annotations

from app.services.content_generation.prompt_payloads import (
    DiagnosticGenerationRequest,
    GeneratedDiagnosticItem,
    GeneratedLesson,
    LessonGenerationRequest,
)
from app.services.llm_provider import (
    AllProvidersFailedError,
    ProviderError,
    build_provider_router,
)
from app.core.config import get_settings


class LLMContentGenerationProvider:
    """Canonical LLM provider that delegates to the Phase 1 provider router."""
    
    provider_name = "llm"
    _router = None

    @classmethod
    def get_router(cls):
        """Get or build the canonical provider router."""
        if cls._router is None:
            cls._router = build_provider_router(get_settings())
        return cls._router

    async def generate_diagnostic_items(
        self,
        request: DiagnosticGenerationRequest,
    ) -> list[GeneratedDiagnosticItem]:
        """Generate diagnostic items using the provider router."""
        from app.services.content_generation.diagnostic_generator import (
            DiagnosticGenerator,
        )
        
        router = self.get_router()
        generator = DiagnosticGenerator(provider_router=router)
        
        return await generator.generate(
            caps_ref=request.caps_ref,
            count=request.count,
            grade=request.grade,
            subject=request.subject,
            subject_code=request.subject_code,
            language=request.language,
        )

    async def generate_lessons(
        self,
        request: LessonGenerationRequest,
    ) -> list[GeneratedLesson]:
        """Generate lessons using the provider router."""
        from app.services.content_generation.lesson_generator import LessonGenerator
        
        router = self.get_router()
        generator = LessonGenerator(provider_router=router)
        
        return await generator.generate(
            caps_ref=request.caps_ref,
            count=request.count,
            grade=request.grade,
            subject=request.subject,
            subject_code=request.subject_code,
            language=request.language,
        )

    async def generate_assessment_blueprints(
        self,
        request: dict,
    ) -> list[dict]:
        """Generate assessment blueprints using the provider router."""
        raise NotImplementedError("Blueprint generation not yet implemented")

    async def generate_study_plan_templates(
        self,
        request: dict,
    ) -> list[dict]:
        """Generate study plan templates using the provider router."""
        raise NotImplementedError("Study plan generation not yet implemented")
