"""Seed V2 IRT item bank with calibrated starter items.

Revision ID: 0005_seed_irt_items
Revises: merge_2026_05_01
Create Date: 2026-05-02
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "0005_seed_irt_items"
down_revision = "merge_2026_05_01"
branch_labels = None
depends_on = None


SUBJECT_TOPICS = {
    "Mathematics": [
        "number sense",
        "patterns",
        "addition and subtraction",
        "measurement",
        "fractions",
        "data handling",
    ],
    "Literacy": [
        "phonics",
        "vocabulary",
        "reading comprehension",
        "sentence structure",
        "writing",
        "listening skills",
    ],
    "Life Skills": [
        "personal wellbeing",
        "community",
        "environment",
        "healthy habits",
        "creative arts",
        "physical education",
    ],
}

LANGUAGE_LABELS = {
    "en": "English",
    "zu": "isiZulu",
    "af": "Afrikaans",
    "xh": "isiXhosa",
}


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS irt_items (
            id VARCHAR(36) PRIMARY KEY,
            grade INTEGER NOT NULL,
            subject VARCHAR(60) NOT NULL,
            topic VARCHAR(120) NOT NULL,
            language VARCHAR(8) NOT NULL DEFAULT 'en',
            question_text TEXT NOT NULL,
            options JSONB NOT NULL,
            correct_option VARCHAR(1) NOT NULL,
            a_param DOUBLE PRECISION NOT NULL DEFAULT 1.0,
            b_param DOUBLE PRECISION NOT NULL DEFAULT 0.0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_irt_grade_subject ON irt_items (grade, subject)")

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
                    difficulty = round(-2.5 + (grade * 0.55) + ((index - 1) * 0.18), 2)
                    discrimination = round(0.75 + ((grade + index) % 6) * 0.18, 2)
                    item_id = f"irt-v2-g{grade}-{_slug(subject)}-{language}-{index}"
                    rows.append(
                        {
                            "id": item_id,
                            "grade": grade,
                            "subject": subject,
                            "topic": topic,
                            "language": language,
                            "question_text": _question_text(grade, subject, topic, language_label, index),
                            "options": json.dumps(_options(subject, grade, index)),
                            "correct_option": "B",
                            "a_param": discrimination,
                            "b_param": max(-3.0, min(3.0, difficulty)),
                        }
                    )
    return rows


def _question_text(grade: int, subject: str, topic: str, language_label: str, index: int) -> str:
    grade_label = "Grade R" if grade == 0 else f"Grade {grade}"
    return (
        f"{grade_label} {subject} calibrated item {index} ({language_label}): "
        f"choose the best answer for {topic}."
    )


def _options(subject: str, grade: int, index: int) -> dict[str, str]:
    if subject == "Mathematics":
        correct = grade + index + 2
        return {
            "A": str(correct - 1),
            "B": str(correct),
            "C": str(correct + 1),
            "D": str(correct + 2),
        }
    if subject == "Literacy":
        return {
            "A": "picture only",
            "B": "best meaning",
            "C": "unrelated word",
            "D": "same sound only",
        }
    return {
        "A": "unsafe choice",
        "B": "responsible choice",
        "C": "unrelated choice",
        "D": "least helpful choice",
    }


def _slug(value: str) -> str:
    return value.lower().replace(" ", "-")
