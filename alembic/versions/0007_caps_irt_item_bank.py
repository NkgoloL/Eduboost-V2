"""Expand the CAPS-aligned IRT item bank across Grades R-7 and core subjects.

Revision ID: 0007_caps_irt_item_bank
Revises: 0006
Create Date: 2026-05-04
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "0007_caps_irt_item_bank"
down_revision = "0006"
branch_labels = None
depends_on = None


SUBJECT_TOPICS: dict[str, tuple[str, ...]] = {
    "Mathematics": ("number sense", "fractions", "measurement", "patterns"),
    "English Home Language": ("phonics", "reading comprehension", "writing", "vocabulary"),
    "English First Additional Language": ("phonics", "oral language", "reading comprehension", "writing"),
    "Life Skills": ("healthy habits", "community", "creative arts", "movement"),
    "Natural Sciences & Technology": ("animals and plants", "materials", "energy", "planet earth"),
    "Social Sciences": ("history", "geography", "maps", "community"),
    "Creative Arts": ("music", "drama", "dance", "visual arts"),
    "Economic & Management Sciences": ("needs and wants", "savings", "markets", "entrepreneurship"),
}

LANGUAGE_LABELS = {
    "en": "English",
    "zu": "isiZulu",
    "af": "Afrikaans",
    "xh": "isiXhosa",
}


def upgrade() -> None:
    rows = _generate_items()
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            INSERT INTO irt_items (
                id, grade, subject, topic, language, question_text, options,
                correct_option, a_param, b_param
            )
            VALUES (
                :id, :grade, :subject, :topic, :language, :question_text,
                CAST(:options AS JSONB), :correct_option, :a_param, :b_param
            )
            ON CONFLICT (id) DO NOTHING
            """
        ),
        rows,
    )


def downgrade() -> None:
    ids = [row["id"] for row in _generate_items()]
    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM irt_items WHERE id = ANY(:ids)"), {"ids": ids})


def _generate_items() -> list[dict]:
    rows: list[dict] = []
    for grade in range(0, 8):
        for subject, topics in SUBJECT_TOPICS.items():
            for language, language_label in LANGUAGE_LABELS.items():
                for index, topic in enumerate(topics, start=1):
                    difficulty = round(max(-3.0, min(3.0, -2.4 + (grade * 0.45) + ((index - 1) * 0.35))), 2)
                    discrimination = round(0.85 + ((grade + index) % 6) * 0.23, 2)
                    rows.append(
                        {
                            "id": f"caps-irt-g{grade}-{_slug(subject)}-{language}-{index}",
                            "grade": grade,
                            "subject": subject,
                            "topic": topic,
                            "language": language,
                            "question_text": _question_text(grade, subject, topic, language_label, index),
                            "options": json.dumps(_options(subject, grade, index)),
                            "correct_option": "B",
                            "a_param": discrimination,
                            "b_param": difficulty,
                        }
                    )
    return rows


def _question_text(grade: int, subject: str, topic: str, language_label: str, index: int) -> str:
    grade_label = "Grade R" if grade == 0 else f"Grade {grade}"
    return (
        f"{grade_label} {subject} item {index} ({language_label}): "
        f"choose the best answer for {topic}."
    )


def _options(subject: str, grade: int, index: int) -> dict[str, str]:
    if subject == "Mathematics":
        correct = grade + index + 3
        return {"A": str(correct - 1), "B": str(correct), "C": str(correct + 1), "D": str(correct + 2)}
    if "English" in subject:
        return {
            "A": "sound only",
            "B": "best meaning",
            "C": "wrong tense",
            "D": "off-topic phrase",
        }
    if subject == "Economic & Management Sciences":
        return {
            "A": "spend all money today",
            "B": "save and plan responsibly",
            "C": "ignore the budget",
            "D": "borrow without thinking",
        }
    return {
        "A": "unsafe choice",
        "B": "best curriculum-aligned choice",
        "C": "partly related choice",
        "D": "least helpful choice",
    }


def _slug(value: str) -> str:
    return value.lower().replace("&", "and").replace(" ", "-")

