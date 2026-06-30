#!/usr/bin/env python3
"""Validate Phase 2 closure-dataset diversity before quality claims are accepted."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate_dataset_payload(payload: dict) -> list[str]:
    cases = payload.get("cases") or []
    errors: list[str] = []
    if payload.get("status") != "approved":
        errors.append("dataset status must be approved")
    if payload.get("closure_eligible") is not True:
        errors.append("closure_eligible must be true")
    if len(cases) < 12:
        errors.append("at least 12 cases are required")
    languages = {str((case.get("filters") or {}).get("language") or "") for case in cases}
    if len({value for value in languages if value}) < 3:
        errors.append("at least 3 languages are required")
    caps_refs = {str((case.get("filters") or {}).get("caps_ref") or "") for case in cases}
    if len({value for value in caps_refs if value}) < 5:
        errors.append("at least 5 CAPS references/strands are required")
    negative = sum(1 for case in cases if not (case.get("expected_chunk_ids") or []))
    if negative < 3:
        errors.append("at least 3 negative/exclusion cases are required")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset")
    args = parser.parse_args()
    payload = json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    errors = validate_dataset_payload(payload)
    cases = payload.get("cases") or []
    languages = {str((case.get("filters") or {}).get("language") or "") for case in cases}
    negative = sum(1 for case in cases if not (case.get("expected_chunk_ids") or []))
    if errors:
        print("Phase 2 closure dataset invalid:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Phase 2 closure dataset valid: {len(cases)} cases, {len(languages)} languages, {negative} negatives")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
