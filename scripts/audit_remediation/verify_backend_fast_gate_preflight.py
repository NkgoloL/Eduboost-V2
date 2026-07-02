#!/usr/bin/env python3
"""Verify prerequisites for Technical Audit Phase 02 backend fast-gate restoration."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def read(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_json(root: Path, rel_path: str) -> dict[str, Any]:
    return json.loads(read(root, rel_path))


def _has_status(text: str, expected: str) -> bool:
    return expected in text


def verify(root: Path = ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    control_path = "docs/roadmap/execution/atlas/phase_02r_start_gate_control.json"
    if not (root / control_path).exists():
        errors.append(f"missing {control_path}")
        control: dict[str, Any] = {}
    else:
        checked.append(control_path)
        control = load_json(root, control_path)
        if control.get("approved_gate") != "2R.8":
            errors.append("Phase 02R must be terminally approved at Gate 2R.8")
        if control.get("authorised_next_gate") is not None:
            errors.append("Phase 02R authorised_next_gate must be null before backend fast remediation")
        if control.get("phase_status") not in {"closed", "complete"}:
            errors.append("Phase 02R phase_status must be closed or complete")

    required_evidence = {
        "baseline reset evidence": "docs/release-evidence/technical-audit/baseline-reset/evidence_index.md",
        "OpenAPI route-contract evidence": "docs/release-evidence/technical-audit/openapi-route-contract/evidence_index.md",
    }
    for label, rel_path in required_evidence.items():
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing {label}: {rel_path}")
            continue
        checked.append(rel_path)
        text = path.read_text(encoding="utf-8")
        if not _has_status(text, "Candidate verification passed"):
            errors.append(f"{label} must record passing candidate verification")
        if not re.search(r"Source commit:.*[0-9a-f]{40}", text):
            errors.append(f"{label} must include a 40-character source commit")

    registry_files = [
        "data/content_factory/scopes.json",
        "data/content_factory/coverage_targets.json",
    ]
    for rel_path in registry_files:
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing Content Factory registry file required for backend fast gate: {rel_path}")
            continue
        checked.append(rel_path)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{rel_path} is not valid JSON: {exc}")
            continue
        if payload in ({}, []):
            warnings.append(f"{rel_path} is present but empty; confirm this is intentional")

    makefile = root / "Makefile"
    if not makefile.exists():
        errors.append("missing Makefile")
    else:
        checked.append("Makefile")
        make_text = makefile.read_text(encoding="utf-8")
        if not re.search(r"^test-fast:\s*$", make_text, re.MULTILINE):
            errors.append("Makefile must expose a test-fast target")
        if "tests/unit" not in make_text:
            errors.append("test-fast target must exercise tests/unit")

    pytest_ini = root / "pytest.ini"
    if not pytest_ini.exists():
        errors.append("missing pytest.ini")
    else:
        checked.append("pytest.ini")

    blocker_register_path = "docs/roadmap/execution/technical_audit_remediation/blocker_register.json"
    if not (root / blocker_register_path).exists():
        errors.append(f"missing {blocker_register_path}")
    else:
        checked.append(blocker_register_path)
        register = load_json(root, blocker_register_path)
        blockers = register.get("remaining_release_blockers_after_reset", [])
        ids = {str(item.get("id")) for item in blockers if isinstance(item, dict)}
        if "TA-BACKEND-FAST-001" not in ids:
            errors.append("blocker register must track TA-BACKEND-FAST-001")
        if "TA-OPENAPI-001" not in ids:
            warnings.append("blocker register no longer lists TA-OPENAPI-001; confirm it was intentionally closed")

    kg_paths = [
        "app/services/curriculum/graph.py",
        "app/services/curriculum/corpus.py",
        "app/services/curriculum/generation.py",
        "app/services/curriculum/tutor_grounding.py",
    ]
    missing_kg_hooks = [rel_path for rel_path in kg_paths if not (root / rel_path).exists()]
    if missing_kg_hooks:
        warnings.append("KG-friendly curriculum grounding hooks missing: " + ", ".join(missing_kg_hooks))
    else:
        checked.extend(kg_paths)

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
        "authority_command": "make test-fast",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = verify(args.root.resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("BACKEND FAST PREFLIGHT PASSED" if result["valid"] else "BACKEND FAST PREFLIGHT FAILED")
        for error in result["errors"]:
            print(f"- {error}")
        for warning in result["warnings"]:
            print(f"warning: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
