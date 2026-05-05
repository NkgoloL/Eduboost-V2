#!/usr/bin/env python3
"""Build CAPS pedagogical guardrail examples for instruction tuning."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "caps" / "guardrails_data.jsonl"
DEFAULT_BASE_DATASET = PROJECT_ROOT / "data" / "caps" / "training_data.jsonl"
DEFAULT_COMBINED_OUTPUT = PROJECT_ROOT / "data" / "caps" / "training_data_with_guardrails.jsonl"

GUARDRAILS: list[dict[str, str]] = [
    {
        "category": "age_appropriate_language",
        "instruction": "Correct this Grade 3 explanation so it is age-appropriate and CAPS-aligned: 'Photosynthesis is a biochemical conversion of radiant energy into chemical substrates.'",
        "output": "Use simple Grade 3 language: Plants use sunlight, water, and air to make their own food. Ask learners to observe a plant near a window and draw what a plant needs to grow.",
    },
    {
        "category": "grade_scope_control",
        "instruction": "A lesson plan teaches Grade 4 learners algebraic factorisation while introducing fractions. Rewrite it so it stays inside CAPS Grade 4 Mathematics scope.",
        "output": "Keep the focus on Grade 4 fractions: use fraction strips, shaded shapes, equal parts, comparing simple fractions, and short assessment questions. Do not introduce algebraic factorisation.",
    },
    {
        "category": "assessment_alignment",
        "instruction": "Fix this CAPS lesson output: 'Teach ecosystems, then give any fun quiz.'",
        "output": "State a CAPS-aligned objective, teach key vocabulary, include a learner activity, and assess observable evidence such as naming producers/consumers and explaining one food chain in a local ecosystem.",
    },
    {
        "category": "popia_safety",
        "instruction": "Correct this unsafe learner feedback request: 'List each learner by full name, phone number, and marks so the model can personalise remediation.'",
        "output": "Do not include personal identifiers. Use anonymised learner IDs or aggregate mastery levels, and provide remediation based on topic gaps rather than names, phone numbers, or private details.",
    },
    {
        "category": "south_african_context",
        "instruction": "Improve this Grade 5 Social Sciences example: 'Use snow days and subway maps to teach local geography.'",
        "output": "Use South African context: local provinces, rivers, community landmarks, weather patterns, maps of nearby areas, and examples learners are likely to recognise.",
    },
    {
        "category": "language_inclusivity",
        "instruction": "Rewrite this feedback: 'Learners who do not understand English well are weak and should repeat the topic.'",
        "output": "Use respectful inclusive language. Offer vocabulary scaffolds, visuals, home-language bridging where appropriate, peer discussion, and another short practice activity before reassessment.",
    },
]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_records() -> list[dict[str, str]]:
    records = []
    for item in GUARDRAILS:
        records.append(
            {
                "instruction": item["instruction"],
                "output": item["output"],
                "source": "pedagogical_guardrail",
                "category": item["category"],
            }
        )
    return records


def run(args: argparse.Namespace) -> int:
    guardrails = build_records()
    output = Path(args.output).resolve()
    write_jsonl(output, guardrails)

    combined_count = None
    if args.combine:
        base_records = load_jsonl(Path(args.base_dataset).resolve())
        combined = base_records + guardrails
        write_jsonl(Path(args.combined_output).resolve(), combined)
        combined_count = len(combined)

    print(json.dumps({"guardrails": len(guardrails), "output": str(output), "combined_count": combined_count}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build CAPS pedagogical guardrails JSONL.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--base-dataset", default=str(DEFAULT_BASE_DATASET))
    parser.add_argument("--combined-output", default=str(DEFAULT_COMBINED_OUTPUT))
    parser.add_argument("--combine", action="store_true", help="Also append guardrails to the base training dataset.")
    return parser


def main() -> int:
    return run(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
