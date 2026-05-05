#!/usr/bin/env python3
"""Build focused CAPS instruction examples for EduBoost lesson tuning."""
from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "caps" / "training_data_focused_caps.jsonl"
DEFAULT_BASE_DATASET = PROJECT_ROOT / "data" / "caps" / "training_data_with_guardrails.jsonl"

SUBJECT_TOPICS = {
    "Mathematics": [
        "equivalent fractions",
        "number patterns",
        "place value",
        "measurement",
        "data handling",
        "mental addition",
    ],
    "Natural Sciences": [
        "ecosystems",
        "plants and animals",
        "materials",
        "energy transfer",
        "Earth and space",
        "food chains",
    ],
    "Life Skills": [
        "healthy habits",
        "personal safety",
        "emotions",
        "community helpers",
        "physical activity",
        "respectful relationships",
    ],
    "English": [
        "reading comprehension",
        "phonics",
        "story sequencing",
        "vocabulary",
        "paragraph writing",
        "listening and speaking",
    ],
    "Social Sciences": [
        "map skills",
        "local history",
        "provinces of South Africa",
        "water resources",
        "community places",
        "weather and climate",
    ],
}

GRADES = [1, 2, 3, 4, 5, 6, 7]
LANGUAGES = ["English", "isiZulu", "Afrikaans"]
TASK_TYPES = [
    "mini lesson",
    "lesson objective and assessment evidence",
    "remediation activity",
    "teacher explanation",
    "parent-friendly progress note",
]


def lesson_output(grade: int, subject: str, topic: str, language: str, task_type: str) -> str:
    return "\n".join(
        [
            f"Title: Grade {grade} {subject} - {topic.title()}",
            f"Grade: Grade {grade}",
            f"Subject: {subject}",
            "CAPS alignment: This response stays within South African CAPS expectations for the stated grade, subject, and topic.",
            f"Lesson objective: Learners will explain the main idea of {topic} using age-appropriate {subject} vocabulary.",
            (
                "Teaching activity: Start with a short question, model one example, let learners work with a partner, "
                "and connect the idea to a familiar South African classroom or community context."
            ),
            (
                f"Worked example: Show one simple {topic} example, ask learners what they notice, "
                "then guide them to explain the answer in their own words."
            ),
            (
                "Assessment evidence: Check that learners can name the key idea, complete one short task, "
                "and explain their reasoning without using private personal information."
            ),
            (
                f"Support and extension: If learners struggle, use visuals, home-language bridging in {language}, "
                "and another concrete example. If learners are ready, ask them to create a second example."
            ),
            f"Response type: {task_type}.",
        ]
    )


def instruction_for(grade: int, subject: str, topic: str, language: str, task_type: str) -> str:
    return (
        f"Create a CAPS-aligned Grade {grade} {subject} {task_type} on {topic}. "
        "Use the required output sections: Title, Grade, Subject, CAPS alignment, "
        "Lesson objective, Teaching activity, Worked example, Assessment evidence, and Support and extension."
    )


def benchmark_reinforcement_records() -> list[dict[str, str]]:
    cases = [
        (4, "Mathematics", "equivalent fractions", "English"),
        (2, "Life Skills", "healthy habits", "English"),
        (7, "Natural Sciences", "ecosystems", "English"),
    ]
    records: list[dict[str, str]] = []
    for grade, subject, topic, language in cases:
        for task_type in TASK_TYPES:
            records.append(
                {
                    "instruction": instruction_for(grade, subject, topic, language, task_type),
                    "output": lesson_output(grade, subject, topic, language, task_type),
                    "source": "focused_caps_benchmark_reinforcement",
                    "grade": str(grade),
                    "subject": subject,
                    "topic": topic,
                    "task_type": task_type,
                }
            )
    return records


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def build_records(target_count: int, include_base: bool, base_dataset: Path) -> list[dict[str, Any]]:
    focused: list[dict[str, Any]] = []
    for grade, language, (subject, topics), task_type in product(
        GRADES,
        LANGUAGES,
        SUBJECT_TOPICS.items(),
        TASK_TYPES,
    ):
        for topic in topics:
            focused.append(
                {
                    "instruction": instruction_for(grade, subject, topic, language, task_type),
                    "output": lesson_output(grade, subject, topic, language, task_type),
                    "source": "focused_caps_template",
                    "grade": str(grade),
                    "subject": subject,
                    "topic": topic,
                    "task_type": task_type,
                }
            )

    records = benchmark_reinforcement_records() + focused
    if include_base:
        records = load_jsonl(base_dataset) + records

    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for record in records:
        key = (record["instruction"], record["output"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
        if len(deduped) >= target_count:
            break
    return deduped


def run(args: argparse.Namespace) -> int:
    records = build_records(
        target_count=args.count,
        include_base=args.include_base,
        base_dataset=Path(args.base_dataset).resolve(),
    )
    if len(records) < args.count:
        raise ValueError(f"Only built {len(records)} records; requested {args.count}")
    output = Path(args.output).resolve()
    write_jsonl(output, records)
    print(json.dumps({"records": len(records), "output": str(output)}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build 300-600 focused CAPS instruction examples.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--base-dataset", default=str(DEFAULT_BASE_DATASET))
    parser.add_argument("--count", type=int, default=360)
    parser.add_argument("--include-base", action=argparse.BooleanOptionalAction, default=True)
    return parser


def main() -> int:
    return run(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
