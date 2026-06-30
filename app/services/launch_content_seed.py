"""Idempotent launch content seed for hosted EduBoost environments."""

from __future__ import annotations

import json
import secrets
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger
from app.core.security import encrypt_pii, hash_email, hash_password
from app.models import Guardian, Language, LearnerProfile, Lesson, UserRole
from app.models.diagnostic_item import DiagnosticItem, ReviewStatusEnum
from app.modules.lessons.lesson_validator import LessonValidator
from app.repositories.item_bank_repository import ItemBankRepository
from app.services.content_scope_registry import ContentScopeRegistry


log = get_logger(__name__)

ROOT = Path(__file__).resolve().parents[2]
LAUNCH_SCOPE_ID = "grade4_mathematics_en"
DEFAULT_ITEM_TARGET = 40
DEFAULT_LESSON_TARGET = 8
SEED_OWNER_EMAIL = "launch-content-seed@example.invalid"
SEED_LEARNER_NAME = "Launch Content Seed Learner"
SEED_LEARNER_GRADE = 4
ADVISORY_LOCK = (443352, 20260525)


async def seed_launch_content_if_needed() -> None:
    """Seed generated launch content when explicitly enabled for production."""
    if not settings.CONTENT_STARTUP_SEED_ENABLED:
        log.info("launch_content_seed_skipped_disabled")
        return
    if not settings.is_production():
        return
    log.warning("launch_content_seed_enabled_explicitly")
    registry = ContentScopeRegistry()
    scope = registry.get_scope(LAUNCH_SCOPE_ID)
    refs = tuple(scope.caps_refs)
    item_bank_path = _artifact_path(scope, "diagnostic_items", "data/generated/items/grade4_maths_launch_item_bank.json")
    lesson_bank_path = _artifact_path(scope, "lessons", "data/generated/lessons/grade4_maths_launch_lessons.json")
    if not item_bank_path.exists() or not lesson_bank_path.exists():
        log.warning(
            "launch_content_seed_artifacts_missing",
            item_bank_exists=item_bank_path.exists(),
            lesson_bank_exists=lesson_bank_path.exists(),
        )
        return

    async with AsyncSessionLocal() as session:
        locked = False
        try:
            locked = await _try_advisory_lock(session)
            if not locked:
                log.info("launch_content_seed_skipped_lock_busy")
                return

            item_target = _target_for(scope, "diagnostic_items.approved", DEFAULT_ITEM_TARGET, registry=registry)
            lesson_target = _target_for(scope, "lessons.approved", DEFAULT_LESSON_TARGET, registry=registry)
            item_counts = await _approved_item_counts(session, refs)
            lesson_counts = await _approved_lesson_counts(session, refs)
            needs_items = any(item_counts.get(ref, 0) < item_target for ref in refs)
            needs_lessons = any(lesson_counts.get(ref, 0) < lesson_target for ref in refs)

            if not needs_items and not needs_lessons:
                log.info(
                    "launch_content_seed_skipped_complete",
                    item_counts=item_counts,
                    lesson_counts=lesson_counts,
                )
                return

            seeded_items = 0
            seeded_lessons = 0
            if needs_items:
                seeded_items = await _seed_items(session, item_bank_path)
            if needs_lessons:
                seeded_lessons = await _seed_lessons(session, lesson_bank_path)

            await session.commit()
            log.info(
                "launch_content_seed_complete",
                seeded_items=seeded_items,
                seeded_lessons=seeded_lessons,
                previous_item_counts=item_counts,
                previous_lesson_counts=lesson_counts,
            )
        except Exception as exc:
            await session.rollback()
            log.warning("launch_content_seed_failed", error=str(exc))
        finally:
            if locked:
                await _release_advisory_lock(session)


async def _try_advisory_lock(session) -> bool:
    if not settings.DATABASE_URL.startswith("postgresql"):
        return True
    result = await session.execute(
        text("SELECT pg_try_advisory_lock(:lock_a, :lock_b)"),
        {"lock_a": ADVISORY_LOCK[0], "lock_b": ADVISORY_LOCK[1]},
    )
    return bool(result.scalar())


async def _release_advisory_lock(session) -> None:
    if not settings.DATABASE_URL.startswith("postgresql"):
        return
    try:
        await session.execute(
            text("SELECT pg_advisory_unlock(:lock_a, :lock_b)"),
            {"lock_a": ADVISORY_LOCK[0], "lock_b": ADVISORY_LOCK[1]},
        )
    except SQLAlchemyError as exc:
        log.warning("launch_content_seed_unlock_failed", error=str(exc))


async def _approved_item_counts(session, refs: tuple[str, ...]) -> dict[str, int]:
    result = await session.execute(
        select(DiagnosticItem.caps_ref, func.count(DiagnosticItem.item_id))
        .where(
            DiagnosticItem.caps_ref.in_(refs),
            DiagnosticItem.review_status == ReviewStatusEnum.APPROVED,
        )
        .group_by(DiagnosticItem.caps_ref)
    )
    return {str(ref): int(count) for ref, count in result.all()}


async def _approved_lesson_counts(session, refs: tuple[str, ...]) -> dict[str, int]:
    result = await session.execute(
        select(Lesson.caps_ref, func.count(Lesson.id))
        .where(Lesson.caps_ref.in_(refs), Lesson.review_status == "approved")
        .group_by(Lesson.caps_ref)
    )
    return {str(ref): int(count) for ref, count in result.all()}


async def _seed_items(session, item_bank_path: Path) -> int:
    payload = json.loads(item_bank_path.read_text(encoding="utf-8"))
    items = [item for item in payload.get("items", []) if item.get("review_status") == "approved"]
    repo = ItemBankRepository(session)
    for item in items:
        await repo.upsert(item)
    return len(items)


async def _seed_lessons(session, lesson_bank_path: Path) -> int:
    payload = json.loads(lesson_bank_path.read_text(encoding="utf-8"))
    lessons = [lesson for lesson in payload.get("lessons", []) if lesson.get("review_status") == "approved"]
    validator = LessonValidator()
    for lesson in lessons:
        result = validator.validate(lesson, require_verified=True)
        if not result.passed:
            raise RuntimeError("Lesson {} failed validation: {}".format(lesson.get("lesson_id"), result.failures))

    learner_id = await _seed_learner_id(session)
    for lesson in lessons:
        row = _lesson_row(lesson, learner_id)
        existing = await session.get(Lesson, row["id"])
        if existing:
            for key, value in row.items():
                setattr(existing, key, value)
        else:
            session.add(Lesson(**row))
    return len(lessons)


async def _seed_learner_id(session) -> str:
    result = await session.execute(select(Guardian).where(Guardian.email_hash == hash_email(SEED_OWNER_EMAIL)))
    guardian = result.scalar_one_or_none()
    if guardian is None:
        guardian = Guardian(
            email_hash=hash_email(SEED_OWNER_EMAIL),
            email_encrypted=encrypt_pii(SEED_OWNER_EMAIL),
            display_name="Launch Content Seed Owner",
            role=UserRole.PARENT,
            password_hash=hash_password(secrets.token_urlsafe(32)),
            is_active=False,
        )
        session.add(guardian)
        await session.flush()

    result = await session.execute(
        select(LearnerProfile).where(
            LearnerProfile.guardian_id == guardian.id,
            LearnerProfile.grade == SEED_LEARNER_GRADE,
            LearnerProfile.display_name == SEED_LEARNER_NAME,
        )
    )
    learner = result.scalar_one_or_none()
    if learner is None:
        learner = LearnerProfile(
            guardian_id=guardian.id,
            display_name=SEED_LEARNER_NAME,
            grade=SEED_LEARNER_GRADE,
            language=Language.ENGLISH,
        )
        session.add(learner)
        await session.flush()
    return learner.id


def _lesson_row(lesson: dict[str, Any], learner_id: str) -> dict[str, Any]:
    return {
        "id": lesson.get("lesson_id"),
        "learner_id": learner_id,
        "grade": lesson["grade"],
        "subject": lesson["subject"],
        "topic": lesson["topic"],
        "content": json.dumps(lesson),
        "caps_ref": lesson["caps_ref"],
        "caps_reference": lesson["caps_ref"],
        "term": lesson.get("term"),
        "subtopic": lesson.get("subtopic"),
        "learning_objectives": lesson.get("learning_objectives", []),
        "explanation": lesson.get("explanation"),
        "worked_examples": lesson.get("worked_examples", []),
        "practice_questions": lesson.get("practice_questions", []),
        "answer_key": lesson.get("answer_key", []),
        "remediation_hints": lesson.get("remediation_hints", []),
        "difficulty_level": lesson.get("difficulty_level"),
        "language_level": lesson.get("language_level"),
        "safety_classification": lesson.get("safety_classification", "safe"),
        "pii_check_passed": bool(lesson.get("pii_check_passed")),
        "answer_key_verified": bool(lesson.get("answer_key_verified")),
        "alignment_confidence": float(lesson.get("alignment_confidence") or 0.0),
        "quality_score": float(lesson.get("quality_score") or 0.0),
        "trust_label": lesson.get("trust_label", {}),
        "review_status": lesson.get("review_status", "approved"),
        "reviewer_id": UUID(lesson["reviewer_id"]) if lesson.get("reviewer_id") else None,
        "prompt_template_version": lesson.get("prompt_template_version"),
        "provider": lesson.get("provider"),
        "model_version": lesson.get("model_version"),
        "generation_latency_ms": int(lesson.get("generation_latency_ms") or 0),
        "token_usage": lesson.get("token_usage", {}),
        "variant_type": lesson.get("variant_type", "standard"),
        "llm_provider": lesson.get("provider", "google"),
    }


def _artifact_path(scope, layer: str, fallback: str) -> Path:
    configured = (scope.artifact_paths or {}).get(layer)
    return ROOT / configured if configured else ROOT / fallback


def _target_for(scope, key: str, default: int, *, registry: ContentScopeRegistry) -> int:
    for target in registry.get_scope_targets(scope.scope_id):
        value = target.targets.get(key)
        if value is not None:
            return int(value)
    return default
