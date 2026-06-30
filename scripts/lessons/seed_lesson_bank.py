#!/usr/bin/env python3
"""Seed approved lesson-bank artifacts into the lessons table for a learner."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import secrets
import sys
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import AsyncSessionLocal
from app.core.security import encrypt_pii, hash_email, hash_password
from app.models import Guardian, Language, LearnerProfile, Lesson, UserRole
from app.modules.lessons.lesson_validator import LessonValidator
from sqlalchemy import select

DEFAULT_INPUT = ROOT / "data" / "generated" / "lessons" / "grade4_maths_launch_lessons.json"


def lesson_row(lesson: dict, learner_id: str) -> dict:
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


async def resolve_seed_learner_id(session, args: argparse.Namespace) -> str:
    if args.learner_id:
        return args.learner_id

    guardian_email = (args.guardian_email or os.getenv("DEV_ADMIN_EMAIL") or "").strip().lower()
    if not guardian_email:
        raise SystemExit("--learner-id or --guardian-email/DEV_ADMIN_EMAIL is required unless --dry-run is used")

    result = await session.execute(select(Guardian).where(Guardian.email_hash == hash_email(guardian_email)))
    guardian = result.scalar_one_or_none()
    if guardian is None:
        if not args.allow_system_seed_owner:
            raise SystemExit(f"Guardian for {guardian_email} was not found; create the admin account before seeding lessons")
        guardian = Guardian(
            email_hash=hash_email(guardian_email),
            email_encrypted=encrypt_pii(guardian_email),
            display_name="Launch Content Seed Owner",
            role=UserRole.PARENT,
            password_hash=hash_password(secrets.token_urlsafe(32)),
            is_active=False,
        )
        session.add(guardian)

    result = await session.execute(
        select(LearnerProfile).where(
            LearnerProfile.guardian_id == guardian.id,
            LearnerProfile.grade == args.seed_learner_grade,
            LearnerProfile.display_name == args.seed_learner_display_name,
        )
    )
    learner = result.scalar_one_or_none()
    if learner is None:
        learner = LearnerProfile(
            guardian_id=guardian.id,
            display_name=args.seed_learner_display_name,
            grade=args.seed_learner_grade,
            language=Language.ENGLISH,
        )
        session.add(learner)
        await session.flush()
    return learner.id


async def seed(args: argparse.Namespace) -> int:
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    lessons = payload.get("lessons", [])
    validator = LessonValidator()
    for lesson in lessons:
        result = validator.validate(lesson, require_verified=True)
        if not result.passed:
            raise SystemExit(f"Lesson {lesson.get('lesson_id')} failed validation: {result.failures}")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "lessons": len(lessons)}, indent=2))
        return 0
    async with AsyncSessionLocal() as session:
        learner_id = await resolve_seed_learner_id(session, args)
        for lesson in lessons:
            row = lesson_row(lesson, learner_id)
            existing = await session.get(Lesson, row["id"])
            if existing:
                for key, value in row.items():
                    setattr(existing, key, value)
            else:
                session.add(Lesson(**row))
        await session.commit()
    print(json.dumps({"seeded": len(lessons), "learner_id": learner_id}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--learner-id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--guardian-email", help="Guardian/admin email used to create or reuse a seed learner when --learner-id is omitted")
    parser.add_argument("--seed-learner-display-name", default="Launch Content Seed Learner")
    parser.add_argument("--seed-learner-grade", type=int, default=4)
    parser.add_argument("--allow-system-seed-owner", action="store_true", help="Create a disabled system guardian/learner owner if the guardian email is absent")
    return asyncio.run(seed(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
