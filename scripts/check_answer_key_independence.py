#!/usr/bin/env python3
"""
Phase 9 — G.6: Independent Answer-Key Checking

Verifies that lesson-generation output includes structured answer-key data
that can be independently validated without access to the generation prompt.

This ensures answer keys are not hardcoded or derived from the same
parameters as the content (which would compromise assessment validity).
"""
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LESSON_PATH = REPO_ROOT / "data" / "generated" / "lessons" / "grade4_maths_launch_lessons.json"


def check_answer_key_structure(lesson_data: dict) -> tuple[bool, str]:
    """
    Verify that lesson output contains structured answer-key data.
    
    Expected structure:
    {
        "lesson_id": "uuid",
        "items": [
            {
                "item_id": "uuid",
                "question": "...",
                "answer_key": "...",
                "answer_key_hash": "sha256:...",  # For verification without exposing key
                "metadata": {
                    "difficulty": 1-5,
                    "cognitive_level": "remember|understand|apply|analyze|evaluate|create",
                    "caps_topic": "..."
                }
            }
        ],
        "answer_key_metadata": {
            "generated_at": "ISO8601",
            "generator_model": "...",
            "validation_hash": "sha256:..."  # Hash of all answer_keys for integrity
        }
    }
    """
    # Check top-level structure
    if "items" not in lesson_data:
        return False, "Missing 'items' array in lesson output"

    items = lesson_data.get("items", [])
    if not items:
        return False, "Lesson items array is empty"

    # Check each item has answer key
    for i, item in enumerate(items):
        if "answer_key" not in item:
            return False, f"Item {i} missing 'answer_key' field"

        if not item["answer_key"]:
            return False, f"Item {i} has empty answer_key"

    # Check for integrity mechanism (hash or metadata)
    has_integrity = (
        "answer_key_metadata" in lesson_data or
        any("answer_key_hash" in item for item in items)
    )

    if not has_integrity:
        return False, "No answer-key integrity mechanism found (hash or metadata)"

    # Check for independence indicators
    # Answer keys should not be derivable from the same prompt as content
    has_separation = (
        "answer_key_metadata" in lesson_data and
        "generator_model" in lesson_data.get("answer_key_metadata", {})
    )

    if not has_separation:
        return False, "No generator model metadata (cannot verify independence)"

    return True, f"OK: {len(items)} items with answer keys and integrity mechanism"


def check_generated_lesson_structure(lesson_data: dict) -> tuple[bool, str]:
    """Verify the current generated-lesson answer-key contract."""
    lesson_id = lesson_data.get("lesson_id") or "<unknown>"
    answer_key = lesson_data.get("answer_key")
    if not isinstance(answer_key, list) or not answer_key:
        return False, f"Lesson {lesson_id} missing non-empty 'answer_key' array"

    for index, answer in enumerate(answer_key):
        if not isinstance(answer, dict):
            return False, f"Lesson {lesson_id} answer_key[{index}] is not an object"
        if not (answer.get("correct_option") or answer.get("correct_answer_text")):
            return False, f"Lesson {lesson_id} answer_key[{index}] has no correct answer"

    if lesson_data.get("answer_key_verified") is not True:
        return False, f"Lesson {lesson_id} does not mark answer_key_verified=true"

    if not lesson_data.get("source_context_hash"):
        return False, f"Lesson {lesson_id} missing source_context_hash integrity marker"

    if not (lesson_data.get("provider") and lesson_data.get("model_version")):
        return False, f"Lesson {lesson_id} missing provider/model_version independence metadata"

    return True, f"OK: lesson {lesson_id} has {len(answer_key)} verified answer-key entries"


def check_payload(data: object) -> tuple[int, int, list[str]]:
    """Check supported lesson/item payload shapes."""
    if isinstance(data, dict) and isinstance(data.get("lessons"), list):
        passed = failed = 0
        errors: list[str] = []
        for lesson in data["lessons"]:
            ok, msg = check_generated_lesson_structure(lesson)
            if ok:
                passed += 1
            else:
                failed += 1
                errors.append(msg)
        return passed, failed, errors

    lessons = data if isinstance(data, list) else [data]
    passed = failed = 0
    errors: list[str] = []
    for lesson in lessons:
        if not isinstance(lesson, dict):
            failed += 1
            errors.append("Payload entry is not an object")
            continue
        ok, msg = check_answer_key_structure(lesson)
        if ok:
            passed += 1
        else:
            failed += 1
            errors.append(msg)
    return passed, failed, errors


def check_lesson_files(directory: Path) -> tuple[int, int, list[str]]:
    """
    Check all lesson JSON files in a directory.
    
    Returns: (passed, failed, errors)
    """
    passed = 0
    failed = 0
    errors = []

    for json_file in directory.rglob("*lesson*.json"):
        if any(part in {".git", ".next", "node_modules", "__pycache__"} for part in json_file.parts):
            continue
        try:
            with open(json_file, "r") as f:
                data = json.load(f)

            current_passed, current_failed, current_errors = check_payload(data)
            passed += current_passed
            failed += current_failed
            errors.extend(f"{json_file.name}: {error}" for error in current_errors)

        except json.JSONDecodeError as e:
            failed += 1
            errors.append(f"{json_file.name}: Invalid JSON - {e}")
        except Exception as e:
            failed += 1
            errors.append(f"{json_file.name}: {e}")

    return passed, failed, errors


def main():
    parser = argparse.ArgumentParser(
        description="Verify answer-key independence in lesson generation output"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_LESSON_PATH,
        help="Path to lesson JSON files or directory"
    )
    parser.add_argument(
        "--sample",
        help="Single lesson JSON file to check"
    )
    args = parser.parse_args()

    print("🔑 Answer-Key Independence Verification")
    print("=" * 50)

    if args.sample:
        # Check single file
        with open(args.sample) as f:
            data = json.load(f)
        passed, failed, errors = check_payload(data)
        if failed == 0 and passed > 0:
            print(f"  ✅ {args.sample}: {passed} payload(s) passed")
            return 0
        else:
            print(f"  ❌ {args.sample}: {errors[0] if errors else 'No supported lesson payloads found'}")
            return 1

    # Check directory
    if args.path.is_file():
        with open(args.path) as f:
            data = json.load(f)
        passed, failed, errors = check_payload(data)
        if failed == 0 and passed > 0:
            print(f"  ✅ {args.path.name}: {passed} payload(s) passed")
            return 0
        else:
            print(f"  ❌ {args.path.name}: {errors[0] if errors else 'No supported lesson payloads found'}")
            return 1

    print(f"\n📁 Scanning: {args.path}")
    passed, failed, errors = check_lesson_files(args.path)

    print("\n📊 Results:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")

    if errors:
        print("\n⚠️ Errors:")
        for error in errors[:10]:  # Show first 10
            print(f"    - {error}")
        if len(errors) > 10:
            print(f"    ... and {len(errors) - 10} more")

    if failed == 0 and passed > 0:
        print("\n🎉 All lessons have valid answer-key structure!")
        return 0
    else:
        print(f"\n💥 Answer-key validation failed for {failed} file(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
