#!/usr/bin/env python3
import os
import json
import asyncio
import asyncpg

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

LANGUAGE_LABELS = {"en": "English", "zu": "isiZulu", "af": "Afrikaans", "xh": "isiXhosa"}


def dsn_from_env():
    db = os.environ.get("DATABASE_URL")
    if not db:
        raise RuntimeError("DATABASE_URL not set")
    if db.startswith("postgresql+asyncpg://"):
        return db.replace("postgresql+asyncpg://", "postgresql://", 1)
    return db


def _slug(value: str) -> str:
    return value.lower().replace(" ", "-")


def _question_text(grade: int, subject: str, topic: str, language_label: str, index: int) -> str:
    grade_label = "Grade R" if grade == 0 else f"Grade {grade}"
    return (
        f"{grade_label} {subject} calibrated item {index} ({language_label}): "
        f"choose the best answer for {topic}."
    )


def _options(subject: str, grade: int, index: int) -> dict:
    if subject == "Mathematics":
        correct = grade + index + 2
        return {"A": str(correct - 1), "B": str(correct), "C": str(correct + 1), "D": str(correct + 2)}
    if subject == "Literacy":
        return {"A": "picture only", "B": "best meaning", "C": "unrelated word", "D": "same sound only"}
    return {"A": "unsafe choice", "B": "responsible choice", "C": "unrelated choice", "D": "least helpful choice"}


def _generate_items(target: int = 1600) -> list[dict]:
    rows: list[dict] = []
    subjects = list(SUBJECT_TOPICS.keys())
    topic_lists = [SUBJECT_TOPICS[s] for s in subjects]
    languages = list(LANGUAGE_LABELS.keys())
    grade = 0
    i = 0
    # Cycle through combinations to generate deterministic unique items
    while len(rows) < target:
        subj_idx = i % len(subjects)
        topic_list = topic_lists[subj_idx]
        topic = topic_list[i % len(topic_list)]
        subject = subjects[subj_idx]
        language = languages[i % len(languages)]
        index = (i // (len(subjects) * len(languages))) % 100 + 1
        # Grow grade slowly across the generated set
        grade = (i // (len(topic_list) * len(languages))) % 13  # grades 0..12

        difficulty = round(-2.5 + (grade * 0.55) + ((index - 1) * 0.18), 2)
        discrimination = round(0.75 + ((grade + index) % 6) * 0.18, 2)
        item_id = f"irt-gen-{len(rows)+1}-g{grade}-{_slug(subject)}-{language}-{index}"
        rows.append(
            {
                "id": item_id,
                "grade": grade,
                "subject": subject,
                "topic": topic,
                "language": language,
                "question_text": _question_text(grade, subject, topic, LANGUAGE_LABELS.get(language, language), index),
                "options": json.dumps(_options(subject, grade, index)),
                "correct_option": "B",
                "a_param": discrimination,
                "b_param": max(-3.0, min(3.0, difficulty)),
            }
        )
        i += 1

    return rows


async def main():
    dsn = dsn_from_env()
    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute(
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
        rows = _generate_items()
        insert_sql = """
            INSERT INTO irt_items (
                id, grade, subject, topic, language, question_text, options,
                correct_option, a_param, b_param
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10) ON CONFLICT (id) DO NOTHING
        """
        for r in rows:
            await conn.execute(
                insert_sql,
                r["id"],
                r["grade"],
                r["subject"],
                r["topic"],
                r["language"],
                r["question_text"],
                r["options"],
                r["correct_option"],
                r["a_param"],
                r["b_param"],
            )
        print('seeded', len(rows), 'irt_items')
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())
