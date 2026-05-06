#!/usr/bin/env python3
"""Build targeted corrective data and benchmarks for the focused CAPS adapter."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = PROJECT_ROOT / "data" / "caps" / "training_data_focused_caps.jsonl"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "caps" / "training_data_focused_caps_v2.jsonl"
DEFAULT_BENCHMARK = PROJECT_ROOT / "tests" / "fixtures" / "llm" / "focused_caps_eval_v2.jsonl"

REQUIRED_SECTIONS = (
    "Title, Grade, Subject, CAPS alignment, Lesson objective, Teaching activity, "
    "Worked example, Assessment evidence, and Support and extension"
)

FOCUS_CASES = [
    {
        "grade": "Grade R",
        "subject": "Life Skills",
        "topic": "colours",
        "task": "play-based learning activity",
        "required": ["grade r", "life skills", "colours", "play", "assessment"],
    },
    {
        "grade": "Grade 5",
        "subject": "Mathematics",
        "topic": "decimals",
        "task": "support and extension activities",
        "required": ["grade 5", "mathematics", "decimals", "support", "extension"],
    },
    {
        "grade": "Grade 7",
        "subject": "Natural Sciences",
        "topic": "ecosystems",
        "task": "lesson objective and assessment evidence",
        "required": ["grade 7", "natural sciences", "ecosystem", "objective", "assessment"],
    },
]

VARIANTS = [
    "mini lesson",
    "remediation activity",
    "teacher explanation",
    "assessment evidence plan",
    "support and extension plan",
    "learner-friendly worked example",
    "parent-friendly summary",
]

ANTI_PATTERNS = [
    "<|user|>",
    "<|assistant|>",
    "<|unexpected|>",
    "<|response|>",
    "short activity",
    "short worked example",
    "same content, structure, and functionality",
    "<div class=",
]


def lesson_output(grade: str, subject: str, topic: str, task: str) -> str:
    topic_phrase = "ecosystem" if topic == "ecosystems" else topic
    method = (
        "play-based learning with songs, sorting games, movement, and colour cards"
        if grade == "Grade R"
        else "a concrete classroom example"
    )
    return "\n".join(
        [
            f"Title: {grade} {subject} - {topic.title()}",
            f"Grade: {grade}",
            f"Subject: {subject}",
            f"CAPS alignment: This {task} is aligned to South African CAPS expectations for {grade} {subject} and focuses clearly on {topic}.",
            f"Lesson objective: Learners will explain {topic_phrase} ideas using age-appropriate {subject} vocabulary and a simple example.",
            (
                f"Teaching activity: Begin with {method} about {topic}, ask learners to describe what they notice, "
                "model the thinking aloud, and let learners practise with a partner before sharing."
            ),
            (
                f"Worked example: Show one clear example of {topic_phrase}. Ask: What is happening? Why does it matter? "
                "Guide learners to answer in a complete sentence."
            ),
            (
                f"Assessment evidence: Learners complete one short task, use the words {topic_phrase} and {subject}, "
                "and explain their answer without sharing private personal information."
            ),
            (
                f"Support and extension: For support, use pictures, objects, home-language bridging, play, and another familiar example. "
                f"For extension, learners create their own {topic_phrase} example and explain it to the class."
            ),
        ]
    )


def instruction_for(grade: str, subject: str, topic: str, task: str) -> str:
    return (
        f"Create a CAPS-aligned {grade} {subject} {task} on {topic}. "
        f"Use the required output sections: {REQUIRED_SECTIONS}."
    )


def corrective_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for case in FOCUS_CASES:
        for variant in VARIANTS:
            records.append(
                {
                    "instruction": instruction_for(case["grade"], case["subject"], case["topic"], variant),
                    "output": lesson_output(case["grade"], case["subject"], case["topic"], variant),
                    "source": "focused_caps_v2_corrective",
                    "grade": case["grade"],
                    "subject": case["subject"],
                    "topic": case["topic"],
                    "task_type": variant,
                }
            )
    for case in FOCUS_CASES:
        bad_output = "\n".join(
            [
                "Bad output to avoid:",
                *ANTI_PATTERNS,
                "",
                "Correct output:",
                lesson_output(case["grade"], case["subject"], case["topic"], case["task"]),
            ]
        )
        records.append(
            {
                "instruction": (
                    f"Rewrite a poor {case['grade']} {case['subject']} response about {case['topic']} "
                    f"so it removes chat markers, HTML, placeholders, and meta commentary. Use {REQUIRED_SECTIONS}."
                ),
                "output": bad_output,
                "source": "focused_caps_v2_artifact_guardrail",
                "grade": case["grade"],
                "subject": case["subject"],
                "topic": case["topic"],
                "task_type": "artifact correction",
            }
        )
    return records


def benchmark_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for case in FOCUS_CASES:
        for variant in VARIANTS[:5]:
            records.append(
                {
                    "id": f"{case['grade'].lower().replace(' ', '-')}-{case['subject'].lower().replace(' ', '-')}-{case['topic'].replace(' ', '-')}-{variant.replace(' ', '-')}",
                    "prompt": instruction_for(case["grade"], case["subject"], case["topic"], variant),
                    "required_terms": case["required"],
                    "forbidden_terms": ["<|user|>", "<|assistant|>", "<|unexpected", "<div", "phone number", "identity number", "university"],
                    "min_words": 80,
                }
            )
    extension_cases = [
        ("Grade 1", "Social Sciences", "map skills", ["grade 1", "social sciences", "map", "objective", "assessment"]),
        ("Grade 3", "Home Language", "reading comprehension", ["grade 3", "home language", "reading", "vocabulary", "assessment"]),
        ("Grade 4", "Natural Sciences", "materials", ["grade 4", "natural sciences", "materials", "worked example", "objective"]),
        ("Grade 6", "Social Sciences", "weather and climate", ["grade 6", "social sciences", "weather", "climate", "assessment"]),
        ("Grade 7", "Mathematics", "integers", ["grade 7", "mathematics", "integers", "remediation", "assessment"]),
    ]
    for grade, subject, topic, required in extension_cases:
        records.append(
            {
                "id": f"{grade.lower().replace(' ', '-')}-{subject.lower().replace(' ', '-')}-{topic.replace(' ', '-')}",
                "prompt": instruction_for(grade, subject, topic, "mini lesson"),
                "required_terms": required,
                "forbidden_terms": ["<|user|>", "<|assistant|>", "<|unexpected", "<div", "phone number", "identity number", "university"],
                "min_words": 80,
            }
        )
    return records


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def dedupe(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, Any]] = []
    for record in records:
        key = (str(record.get("instruction", "")), str(record.get("output", "")))
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


def run(args: argparse.Namespace) -> int:
    source_records = load_jsonl(Path(args.source).resolve())
    records = dedupe(corrective_records() * args.corrective_multiplier + source_records)
    write_jsonl(Path(args.output).resolve(), records)
    benchmarks = benchmark_records()
    write_jsonl(Path(args.benchmark_output).resolve(), benchmarks)
    print(
        json.dumps(
            {
                "benchmark_records": len(benchmarks),
                "corrective_records": len(corrective_records()) * args.corrective_multiplier,
                "output": str(Path(args.output).resolve()),
                "records": len(records),
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build v2 corrective CAPS training data and benchmarks.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--benchmark-output", default=str(DEFAULT_BENCHMARK))
    parser.add_argument("--corrective-multiplier", type=int, default=4)
    return parser


def main() -> int:
    return run(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
