"""
EduBoost SA — Lessons Router (V2)
LLM-generated adaptive lessons. Consent gate applied at router level.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id, require_active_consent
from app.modules.lessons.llm_gateway import LLMGateway
from app.repositories import DiagnosticRepository, LessonRepository

router = APIRouter(prefix="/lessons", tags=["Lessons"])
_llm = LLMGateway()
_lesson_repo = LessonRepository()
_diagnostic_repo = DiagnosticRepository()


class GenerateLessonRequest(BaseModel):
    learner_id: UUID
    subject: str
    topic: str
    language: str = "en"


@router.post(
    "/generate",
    status_code=status.HTTP_201_CREATED,
)
async def generate_lesson(
    body: GenerateLessonRequest,
    _user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.core.security import pseudonymise_for_llm
    from app.core.metrics import lessons_generated_total

    await require_active_consent(body.learner_id, db)

    # Get ability level from latest diagnostic (null-safe)
    latest_diag = await _diagnostic_repo.get_latest_for_learner(
        body.learner_id, body.subject, db
    )
    ability = float(latest_diag.ability_estimate or 0.0) if latest_diag else 0.0

    # Pseudonymise learner — NEVER send real UUID to LLM provider
    pseudonym = pseudonymise_for_llm(body.learner_id)

    prompt = _build_lesson_prompt(
        subject=body.subject,
        topic=body.topic,
        language=body.language,
        ability=ability,
        pseudonym=pseudonym,
    )

    response = await _llm.generate(
        prompt,
        system=_LESSON_SYSTEM_PROMPT,
        language=body.language,
        max_tokens=1200,
    )

    lesson = await _lesson_repo.create(
        db,
        learner_id=body.learner_id,
        subject=body.subject,
        grade="",  # Populated from learner profile in full implementation
        language=body.language,
        topic=body.topic,
        content=response.content,
        llm_provider=response.provider,
        prompt_tokens=response.prompt_tokens,
        completion_tokens=response.completion_tokens,
        ability_level=ability,
    )

    lessons_generated_total.labels(
        grade="", subject=body.subject, language=body.language
    ).inc()

    return {
        "id": str(lesson.id),
        "topic": lesson.topic,
        "content": lesson.content,
        "provider": lesson.llm_provider,
        "created_at": lesson.created_at.isoformat(),
    }


@router.get(
    "/{learner_id}",
    dependencies=[Depends(require_active_consent)],
)
async def get_lessons(
    learner_id: UUID,
    subject: str | None = None,
    limit: int = 10,
    _user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    lessons = await _lesson_repo.get_recent_for_learner(
        learner_id, db, subject=subject, limit=limit
    )
    return [
        {
            "id": str(l.id),
            "subject": l.subject,
            "topic": l.topic,
            "language": l.language,
            "created_at": l.created_at.isoformat(),
        }
        for l in lessons
    ]


_LESSON_SYSTEM_PROMPT = (
    "You are a South African Grade R-7 educational assistant. "
    "Generate clear, engaging, age-appropriate lessons aligned to the CAPS curriculum. "
    "Use simple, encouraging language. Never include learner personal information. "
    "Format your response in clean markdown."
)


def _build_lesson_prompt(
    *,
    subject: str,
    topic: str,
    language: str,
    ability: float,
    pseudonym: str,
) -> str:
    from app.modules.diagnostics.irt_engine import IRTEngine
    band = IRTEngine.interpret_ability(ability)
    lang_name = {"en": "English", "zu": "isiZulu", "xh": "isiXhosa", "af": "Afrikaans"}.get(language, "English")

    return (
        f"Create a {band['label'].lower()}-level lesson on '{topic}' in {subject} "
        f"for a South African learner. "
        f"Write the lesson in {lang_name}. "
        f"The learner is at the {band['label']} level ({band['emoji']}). "
        f"Include: a clear explanation, 2-3 worked examples, and 3 practice questions. "
        f"Keep it encouraging and age-appropriate for the CAPS curriculum."
    )
