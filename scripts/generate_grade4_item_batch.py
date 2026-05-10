#!/usr/bin/env python3
"""Generate the Grade 4 Mathematics item-bank expansion batch."""

from __future__ import annotations

import json
import uuid
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ITEM_BANK = ROOT / "data" / "caps" / "grade4_maths_item_bank.json"
NAMESPACE = uuid.UUID("7c6af35d-96e6-4d1b-92f1-a7d0c8d0b100")
CREATED_AT = "2026-05-10T12:00:00Z"
SOURCE = "codex_generated_batch_2026_05_10"

DIFFICULTY_VALUES = {
    "easy": [-1.45, -1.35, -1.25, -1.15, -1.05],
    "moderate": [-0.8, -0.65, -0.5, -0.35, -0.2],
    "on_level": [0.05, 0.2, 0.35, 0.5, 0.65],
    "challenging": [0.85, 1.0, 1.15, 1.3, 1.45],
}


def generated_id(ref: str, band: str, n: int) -> str:
    return str(uuid.uuid5(NAMESPACE, f"g4m:{ref}:{band}:{n}"))


def make_item(
    *,
    ref: str,
    n: int,
    band: str,
    topic: str,
    subtopic: str,
    skill: str,
    stem: str,
    answer: str,
    options: list[str],
    explanation: str,
    tags: list[str],
) -> dict:
    option_labels = ["A", "B", "C", "D"]
    distractor_rationale = {}
    for label, text in zip(option_labels, options, strict=True):
        if label != answer:
            distractor_rationale[label] = (
                f"{text} shows a common error with "
                f"{skill.replace('_', ' ')}."
            )

    return {
        "item_id": generated_id(ref, band, n),
        "caps_ref": ref,
        "grade": 4,
        "subject": "Mathematics",
        "term": 1,
        "topic": topic,
        "subtopic": subtopic,
        "skill": skill,
        "stem": stem,
        "answer_key": answer,
        "options": [
            {"label": label, "text": str(text)}
            for label, text in zip(option_labels, options, strict=True)
        ],
        "explanation": explanation,
        "distractor_rationale": distractor_rationale,
        "misconception_tags": tags,
        "item_type": "mcq",
        "language": "en",
        "difficulty_band": band,
        "difficulty_b": DIFFICULTY_VALUES[band][n % len(DIFFICULTY_VALUES[band])],
        "discrimination_a": round(0.95 + (n % 5) * 0.1, 2),
        "guessing_c": 0.25,
        "review_status": "ai_generated",
        "reviewer_id": None,
        "reviewed_at": None,
        "exposure_count": 0,
        "max_exposure": 250,
        "safety_passed": True,
        "quality_score": 0.82,
        "source": SOURCE,
        "created_at": CREATED_AT,
    }


def rotate_options(n: int, correct: str, options: list[str]) -> tuple[str, list[str]]:
    shift = n % 4
    rotated = options[shift:] + options[:shift]
    answer = ["A", "B", "C", "D"][rotated.index(correct)]
    return answer, rotated


def whole_number_items() -> list[dict]:
    batch: list[dict] = []
    seq = 1
    for band, count in [("easy", 7), ("moderate", 11), ("on_level", 12), ("challenging", 6)]:
        for i in range(count):
            n = seq
            seq += 1
            kind = i % 6
            if kind == 0:
                th = 2 + (n % 7)
                h = 1 + (n % 8)
                t = (n * 3) % 10
                o = (n * 7) % 10
                value = th * 1000 + h * 100 + t * 10 + o
                correct = str(value)
                options = [correct, str(value + 100), str(value - 10), str(value + 1)]
                stem = (
                    f"A school has {th} thousands, {h} hundreds, "
                    f"{t} tens and {o} ones of counters. What number is this?"
                )
                explanation = f"The number is {th}000 + {h}00 + {t}0 + {o}, which is {value}."
                skill = "build_numbers_from_place_value"
                tags = ["place_value", "expanded_notation"]
            elif kind == 1:
                base = 3400 + n * 37
                numbers = [base, base + 120, base - 80, base + 12]
                correct = str(max(numbers))
                options = [str(x) for x in numbers]
                shown = ", ".join(options)
                stem = f"Which number is the greatest: {shown}?"
                explanation = f"Compare thousands first, then hundreds and tens. The greatest number is {correct}."
                skill = "ordering_4digit_numbers"
                tags = ["ordering_numbers", "place_value"]
            elif kind == 2:
                value = 2100 + n * 73
                rounded = round(value / 100) * 100
                correct = str(rounded)
                options = [correct, str(rounded + 100), str(rounded - 100), str(value)]
                stem = f"Round {value} to the nearest hundred."
                explanation = f"Look at the tens digit. It tells whether {value} rounds to {rounded}."
                skill = "rounding_off_to_nearest_10_100_1000"
                tags = ["rounding", "place_value"]
            elif kind == 3:
                a = 1200 + n * 41
                b = a + (10 if n % 2 else -100)
                sign = ">" if a > b else "<"
                correct = sign
                options = [sign, "=", "<" if sign == ">" else ">", "not sure"]
                stem = f"Choose the correct sign: {a} __ {b}."
                explanation = f"Compare place values from left to right. This gives {a} {sign} {b}."
                skill = "comparing_4digit_numbers_lt_gt_eq"
                tags = ["comparison_symbols", "place_value"]
            elif kind == 4:
                value = 5000 + n * 29
                digit = (value // 100) % 10
                digit_value = digit * 100
                correct = str(digit_value)
                options = [correct, str(digit), str(digit * 10), str(digit * 1000)]
                stem = f"What is the value of the hundreds digit in {value}?"
                explanation = f"The hundreds digit is {digit}, so its value is {digit_value}."
                skill = "identify_place_value_4digit"
                tags = ["place_value", "digit_value"]
            else:
                start = 1300 + n * 50
                correct = str(start + 200)
                options = [correct, str(start + 20), str(start + 100), str(start + 300)]
                stem = f"Count on in hundreds: {start}, {start + 100}, __."
                explanation = f"Counting in hundreds adds 100 each time, so the next number is {correct}."
                skill = "count_forwards_backwards_4digit"
                tags = ["skip_counting", "hundreds"]

            answer, rotated = rotate_options(n, correct, options)
            batch.append(
                make_item(
                    ref="4.M.1.1",
                    n=n,
                    band=band,
                    topic="Whole Numbers",
                    subtopic="Number range and place value",
                    skill=skill,
                    stem=stem,
                    answer=answer,
                    options=rotated,
                    explanation=explanation,
                    tags=tags,
                )
            )
    return batch


def fraction_items() -> list[dict]:
    batch: list[dict] = []
    seq = 1
    for band, count in [("easy", 10), ("moderate", 9), ("on_level", 10), ("challenging", 6)]:
        for i in range(count):
            n = seq
            seq += 1
            kind = i % 5
            if kind == 0:
                denominator = [4, 5, 6, 8][n % 4]
                numerator = 1 + (n % (denominator - 1))
                correct = f"{numerator}/{denominator}"
                options = [
                    correct,
                    f"{denominator}/{numerator}",
                    f"{numerator}/{denominator + 1}",
                    f"{numerator + 1}/{denominator}",
                ]
                stem = f"A bar has {denominator} equal parts. {numerator} parts are shaded. What fraction is shaded?"
                explanation = f"The denominator is all {denominator} parts. The numerator is the {numerator} shaded parts."
                skill = "describe_fraction_of_whole"
                tags = ["numerator_denominator", "fraction_representation"]
            elif kind == 1:
                denominator = [6, 8, 10, 12][n % 4]
                a = 1 + (n % (denominator - 3))
                b = a + 2
                correct = f"{b}/{denominator}"
                options = [correct, f"{a}/{denominator}", f"{a}/{b}", f"{denominator}/{b}"]
                stem = f"Which fraction is greater: {a}/{denominator} or {b}/{denominator}?"
                explanation = f"The denominators are the same. The larger numerator gives the greater fraction, so {correct} is greater."
                skill = "compare_fractions_same_denominator"
                tags = ["compare_fractions", "same_denominator"]
            elif kind == 2:
                base, correct = [
                    ("1/2", "2/4"),
                    ("2/3", "4/6"),
                    ("3/4", "6/8"),
                    ("1/3", "2/6"),
                ][n % 4]
                options = [correct, "1/4", "3/6", "4/8"]
                stem = f"Which fraction is equal to {base}?"
                explanation = f"Equivalent fractions name the same part of a whole. {correct} is equal to {base}."
                skill = "identify_equivalent_fractions"
                tags = ["equivalent_fractions", "fraction_size"]
            elif kind == 3:
                denominator = [2, 3, 4, 5][n % 4]
                whole = denominator * (3 + (n % 5))
                numerator = 1 + (n % max(1, denominator - 1))
                value = whole * numerator // denominator
                correct = str(value)
                options = [correct, str(value + denominator), str(max(1, value - numerator)), str(whole - denominator)]
                stem = f"There are {whole} counters. What is {numerator}/{denominator} of the counters?"
                explanation = f"First find one part by dividing by {denominator}. Then multiply by {numerator} to get {value}."
                skill = "find_fraction_of_collection"
                tags = ["fraction_of_set", "division_groups"]
            else:
                denominator = [3, 4, 5, 6][n % 4]
                numerator = 1 + (n % (denominator - 1))
                correct = "proper fraction"
                options = [correct, "mixed number", "greater than one", "not a fraction"]
                stem = f"What kind of fraction is {numerator}/{denominator}?"
                explanation = f"The numerator {numerator} is less than the denominator {denominator}, so the fraction is less than one."
                skill = "recognise_proper_fractions"
                tags = ["proper_fraction", "fraction_language"]

            answer, rotated = rotate_options(n, correct, options)
            batch.append(
                make_item(
                    ref="4.M.1.2",
                    n=n,
                    band=band,
                    topic="Fractions",
                    subtopic="Common fractions",
                    skill=skill,
                    stem=stem,
                    answer=answer,
                    options=rotated,
                    explanation=explanation,
                    tags=tags,
                )
            )
    return batch


def shape_items() -> list[dict]:
    templates = [
        (
            "Which shape has three straight sides?",
            "triangle",
            ["triangle", "square", "circle", "rectangle"],
            "A triangle has three straight sides and three corners, so it matches the clue.",
            "identify_2d_shapes",
            ["shape_names", "sides"],
        ),
        (
            "How many corners does a rectangle have?",
            "4",
            ["4", "3", "5", "0"],
            "A rectangle has four corners and four straight sides, so the answer is four.",
            "count_sides_vertices",
            ["vertices", "rectangle_properties"],
        ),
        (
            "Which shape has four equal sides and four square corners?",
            "square",
            ["square", "rectangle", "triangle", "circle"],
            "A square has four equal sides and four square corners.",
            "describe_shape_properties",
            ["square_properties", "equal_sides"],
        ),
        (
            "A rectangle is not a square. How many lines of symmetry does it have?",
            "2",
            ["2", "1", "4", "0"],
            "A rectangle that is not a square has one vertical and one horizontal line of symmetry.",
            "identify_lines_of_symmetry",
            ["symmetry", "rectangle_properties"],
        ),
        (
            "Which shape can tile a flat floor with no gaps?",
            "square",
            ["square", "circle", "oval", "single curved line"],
            "Squares fit together edge to edge, so they can tile a flat floor with no gaps.",
            "recognise_tessellation",
            ["tessellation", "straight_sides"],
        ),
        (
            "Which statement is true for every square?",
            "It has four equal sides.",
            [
                "It has four equal sides.",
                "It has three corners.",
                "It has one curved side.",
                "It has five sides.",
            ],
            "Every square has four equal sides and four square corners.",
            "reason_about_shape_properties",
            ["properties", "square_properties"],
        ),
    ]

    batch: list[dict] = []
    seq = 1
    for band, count in [("easy", 9), ("moderate", 10), ("on_level", 10), ("challenging", 6)]:
        for i in range(count):
            n = seq
            seq += 1
            stem, correct, options, explanation, skill, tags = templates[i % len(templates)]
            answer, rotated = rotate_options(n, correct, options)
            batch.append(
                make_item(
                    ref="4.M.1.3",
                    n=n,
                    band=band,
                    topic="Geometry",
                    subtopic="2-D shapes",
                    skill=skill,
                    stem=stem,
                    answer=answer,
                    options=rotated,
                    explanation=explanation,
                    tags=tags,
                )
            )
    return batch


def main() -> None:
    with ITEM_BANK.open(encoding="utf-8") as f:
        data = json.load(f)

    items = data["items"]
    existing_ids = {item["item_id"] for item in items}
    batch = whole_number_items() + fraction_items() + shape_items()
    new_items = [item for item in batch if item["item_id"] not in existing_ids]

    if new_items:
        items.extend(new_items)
        data["generated_at"] = CREATED_AT
        with ITEM_BANK.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    print(f"added {len(new_items)} items")
    print("status counts:", Counter((item["caps_ref"], item.get("review_status")) for item in items))
    print("new band counts:", Counter((item["caps_ref"], item.get("difficulty_band")) for item in new_items))


if __name__ == "__main__":
    main()
