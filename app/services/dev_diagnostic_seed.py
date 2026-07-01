"""Deterministic non-production diagnostic item seeding for dev-session E2E.

This helper is intentionally called only from `/auth/dev-session`, which is
already unavailable in production. It seeds a tiny Grade 3 item bank so the
backend-backed seeded diagnostic journey can fetch real FastAPI/Postgres
diagnostic items without relying on AI generation or external content jobs.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.item_bank_repository import ItemBankRepository

DEV_DIAGNOSTIC_REVIEWER_ID = UUID("00000000-0000-4000-8000-0000000016c3")


def _item(
    item_id: str,
    *,
    caps_ref: str,
    subject: str,
    topic: str,
    skill: str,
    stem: str,
    answer_key: str,
    options: dict[str, str],
    difficulty_b: float,
) -> dict:
    return {
        "item_id": item_id,
        "caps_ref": caps_ref,
        "grade": 3,
        "subject": subject,
        "term": 1,
        "topic": topic,
        "subtopic": skill,
        "skill": skill,
        "stem": stem,
        "answer_key": answer_key,
        "options": [{"key": key, "label": value} for key, value in options.items()],
        "explanation": f"The correct answer is {answer_key}.",
        "distractor_rationale": [],
        "misconception_tags": [],
        "item_type": "mcq",
        "language": "en",
        "difficulty_b": difficulty_b,
        "discrimination_a": 1.0,
        "guessing_c": 0.25,
        "difficulty_band": "on_level",
        "review_status": "approved",
        "reviewer_id": DEV_DIAGNOSTIC_REVIEWER_ID,
        "reviewed_at": datetime.now(timezone.utc),
        "exposure_count": 0,
        "max_exposure": 1000,
        "quality_score": 0.95,
        "safety_passed": True,
        "source": "human_authored",
        "irt_quality_state": "healthy",
        "irt_model_version": "phase16c-dev-seed",
        "irt_policy_version": "phase16c-dev-seed-v1",
    }


DEV_DIAGNOSTIC_ITEMS = [
    _item(
        "00000000-0000-4000-8000-000000160301",
        caps_ref="CAPS:G3:MATHEMATICS:T1:NUMBERS:COUNTING",
        subject="Mathematics",
        topic="Numbers, Operations and Relationships",
        skill="Counting and comparing whole numbers",
        stem="Which number is the same as 30 + 4?",
        answer_key="B",
        options={"A": "31", "B": "34", "C": "43", "D": "304"},
        difficulty_b=-0.8,
    ),
    _item(
        "00000000-0000-4000-8000-000000160302",
        caps_ref="CAPS:G3:MATHEMATICS:T1:NUMBERS:ADDITION",
        subject="Mathematics",
        topic="Numbers, Operations and Relationships",
        skill="Addition within 100",
        stem="What is 27 + 15?",
        answer_key="C",
        options={"A": "32", "B": "40", "C": "42", "D": "52"},
        difficulty_b=-0.2,
    ),
    _item(
        "00000000-0000-4000-8000-000000160303",
        caps_ref="CAPS:G3:MATHEMATICS:T1:PATTERNS:NUMBER_PATTERNS",
        subject="Mathematics",
        topic="Patterns, Functions and Algebra",
        skill="Complete a simple number pattern",
        stem="What comes next? 5, 10, 15, 20, __",
        answer_key="D",
        options={"A": "21", "B": "22", "C": "24", "D": "25"},
        difficulty_b=0.1,
    ),
    _item(
        "00000000-0000-4000-8000-000000160304",
        caps_ref="CAPS:G3:MATHEMATICS:T1:MEASUREMENT:MONEY",
        subject="Mathematics",
        topic="Measurement",
        skill="Work with South African rand values",
        stem="A pencil costs R3 and a ruler costs R6. How much do they cost together?",
        answer_key="A",
        options={"A": "R9", "B": "R6", "C": "R3", "D": "R18"},
        difficulty_b=0.3,
    ),
    _item(
        "00000000-0000-4000-8000-000000160305",
        caps_ref="CAPS:G3:MATHEMATICS:T1:DATA:PICTOGRAPHS",
        subject="Mathematics",
        topic="Data Handling",
        skill="Read simple data totals",
        stem="Sipho read 4 books and Lerato read 6 books. How many books did they read altogether?",
        answer_key="C",
        options={"A": "2", "B": "8", "C": "10", "D": "12"},
        difficulty_b=0.5,
    ),
    _item(
        "00000000-0000-4000-8000-000000160306",
        caps_ref="CAPS:G3:ENGLISH:T1:READING:COMPREHENSION",
        subject="English",
        topic="Reading and Viewing",
        skill="Identify a main idea",
        stem="A story is mostly about a dog finding its way home. What is the main idea?",
        answer_key="B",
        options={"A": "A cat sleeps", "B": "A dog goes home", "C": "A shop opens", "D": "A bus is late"},
        difficulty_b=-0.1,
    ),
]


async def seed_dev_diagnostic_items(db: AsyncSession, *, grade: int = 3) -> int:
    """Upsert deterministic dev diagnostic items and return the count touched."""
    repo = ItemBankRepository(db)
    count = 0
    for payload in DEV_DIAGNOSTIC_ITEMS:
        if int(payload["grade"]) == int(grade):
            await repo.upsert(payload)
            count += 1
    await db.flush()
    return count


__all__ = ["DEV_DIAGNOSTIC_ITEMS", "seed_dev_diagnostic_items"]
