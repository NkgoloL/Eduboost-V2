#!/usr/bin/env python3
"""Validate the bounded Phase 2R Grade 4 Mathematics source inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTER = ROOT / "data/curriculum/registries/grade4_mathematics_caps_source_completeness.json"
REQUIRED_LANGUAGES = {"en", "af", "nso"}
REQUIRED_TERMS = {1, 2, 3, 4}
REQUIRED_STRANDS = {
    "Numbers, Operations and Relationships",
    "Patterns, Functions and Algebra",
    "Space and Shape",
    "Measurement",
    "Data Handling",
}
RESOLVED_STATUSES = {"located", "absence_approved"}
VALID_ITEM_STATUSES = RESOLVED_STATUSES | {"pending", "rejected"}


def canonical_hash(document: dict[str, Any]) -> str:
    payload = dict(document)
    payload.pop("manifest_sha256", None)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate(document: dict[str, Any], *, require_frozen: bool) -> list[str]:
    errors: list[str] = []
    if document.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if document.get("inventory_code") != "grade4_mathematics_caps_first_closure":
        errors.append("unexpected inventory_code")
    if not isinstance(document.get("version_number"), int) or document["version_number"] < 1:
        errors.append("version_number must be a positive integer")

    expected_hash = canonical_hash(document)
    if document.get("manifest_sha256") != expected_hash:
        errors.append("manifest_sha256 does not match the canonical register payload")

    scope = document.get("scope") or {}
    if scope.get("curriculum") != "CAPS" or scope.get("grade") != 4 or scope.get("subject") != "Mathematics":
        errors.append("scope must be CAPS Grade 4 Mathematics")
    if set(scope.get("terms") or []) != REQUIRED_TERMS:
        errors.append("scope must contain Terms 1-4")
    if set(scope.get("strands") or []) != REQUIRED_STRANDS:
        errors.append("scope must contain all five required strands")
    if set(scope.get("delivery_languages") or []) != REQUIRED_LANGUAGES:
        errors.append("scope must contain delivery languages en, af, and nso")

    items = document.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty list")
        items = []

    codes: set[str] = set()
    strand_coverage: set[str] = set()
    language_records: set[str] = set()
    for index, item in enumerate(items):
        prefix = f"items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        code = item.get("requirement_code")
        if not isinstance(code, str) or not code.strip():
            errors.append(f"{prefix}.requirement_code is required")
        elif code in codes:
            errors.append(f"duplicate requirement_code: {code}")
        else:
            codes.add(code)

        status = item.get("item_status")
        if status not in VALID_ITEM_STATUSES:
            errors.append(f"{prefix}.item_status is invalid")
        if item.get("authority_tier") not in {"tier_1", "tier_2", "tier_3"}:
            errors.append(f"{prefix}.authority_tier is invalid")
        language = item.get("language")
        if language is not None and language not in REQUIRED_LANGUAGES:
            errors.append(f"{prefix}.language is invalid")
        if language in REQUIRED_LANGUAGES:
            language_records.add(language)

        strand = item.get("strand")
        if strand is not None and strand not in REQUIRED_STRANDS:
            errors.append(f"{prefix}.strand is invalid")
        if (
            item.get("requirement_type") == "strand_authority"
            and item.get("authority_tier") == "tier_1"
            and status == "located"
            and strand in REQUIRED_STRANDS
        ):
            strand_coverage.add(strand)

        if status == "located":
            if not item.get("source_id") or not item.get("source_version_id"):
                errors.append(f"{prefix} located item requires source_id and source_version_id")
        if status == "absence_approved":
            for field in ("absence_reason", "reviewed_by", "reviewed_at"):
                if not item.get(field):
                    errors.append(f"{prefix} absence_approved item requires {field}")

    if not REQUIRED_LANGUAGES.issubset(language_records):
        errors.append("inventory requires an explicit record for en, af, and nso")

    if require_frozen:
        if document.get("status") != "frozen":
            errors.append("closure requires status=frozen")
        if not document.get("frozen_by") or not document.get("frozen_at"):
            errors.append("closure requires frozen_by and frozen_at")
        unresolved = [str(item.get("requirement_code")) for item in items if item.get("item_status") not in RESOLVED_STATUSES]
        if unresolved:
            errors.append(f"closure inventory has unresolved items: {', '.join(sorted(unresolved))}")
        if strand_coverage != REQUIRED_STRANDS:
            missing = sorted(REQUIRED_STRANDS - strand_coverage)
            errors.append(f"Tier 1 located evidence is missing for strands: {', '.join(missing)}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--require-frozen", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        document = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Unable to load source-completeness register: {exc}", file=sys.stderr)
        return 1

    errors = validate(document, require_frozen=args.require_frozen)
    result = {
        "path": str(args.path.relative_to(ROOT) if args.path.is_relative_to(ROOT) else args.path),
        "status": document.get("status"),
        "manifest_sha256": document.get("manifest_sha256"),
        "require_frozen": args.require_frozen,
        "valid": not errors,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif errors:
        print("Source-completeness register validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print(f"Source-completeness register valid ({document.get('status')})")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
