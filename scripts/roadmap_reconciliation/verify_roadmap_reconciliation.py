#!/usr/bin/env python3
"""Verify the Roadmap Reconciliation Slice evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any

RECORD_PATH = pathlib.Path("docs/roadmap/reconciliation/roadmap_reconciliation_record.json")
SOURCES_PATH = pathlib.Path("docs/roadmap/reconciliation/canonical_roadmap_sources.json")
OUTSTANDING_REGISTER_PATH = pathlib.Path("docs/roadmap/reconciliation/outstanding_work_register.md")
CLASSIFICATION_PATH = pathlib.Path("docs/roadmap/reconciliation/phase_18_to_21_governance_classification.md")
FREEZE_PATH = pathlib.Path("docs/roadmap/reconciliation/roadmap_new_work_freeze.md")

REQUIRED_FALSE_FIELDS: tuple[str, ...] = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "new_unreconciled_work_authorised",
    "runtime_kg_implementation_claimed",
)
REQUIRED_TRUE_FIELDS: tuple[str, ...] = (
    "roadmap_reconciliation_claimed",
    "roadmap_reconciliation_recorded",
    "canonical_sources_valid",
    "outstanding_work_register_valid",
    "phase_18_to_21_classified_as_auxiliary_governance",
    "new_work_freeze_active",
    "next_work_must_cite_outstanding_work_register",
)
REQUIRED_RR_IDS: tuple[str, ...] = tuple(f"RR-{i:03d}" for i in range(1, 19))
REQUIRED_SOURCE_PATHS: tuple[str, ...] = (
    "docs/roadmap/PHASE_STATUS_REGISTER.md",
    "docs/roadmap/roadmap.md",
    "docs/product/roadmap.md",
    "docs/operations/todo_implementation_plan.md",
    "docs/roadmap/post_baseline_roadmap_register.md",
    "docs/current_state.md",
    "docs/release/EduBoost_V2_North_Star_TODO.md",
)
REQUIRED_RAW_FILES: tuple[str, ...] = (
    "raw/git_state.json",
    "raw/canonical_roadmap_sources_snapshot.json",
    "raw/source_hashes.json",
    "raw/outstanding_work_register_snapshot.md",
    "raw/phase_18_to_21_governance_classification_snapshot.md",
    "raw/roadmap_new_work_freeze_snapshot.md",
    "raw/roadmap_reconciliation_result.json",
    "raw/roadmap_reconciliation_record_snapshot.json",
)


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sha256sums(sums_path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    if not sums_path.exists():
        return [f"SHA256SUMS file missing: {sums_path}"]
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, file_name = line.split("  ", 1)
        except ValueError:
            errors.append(f"malformed SHA256SUMS line: {line}")
            continue
        path = pathlib.Path(file_name)
        if not path.exists():
            errors.append(f"SHA target missing: {path}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            errors.append(f"SHA mismatch for {path}: expected {expected}, got {actual}")
    return errors


def validate_sources_file(path: pathlib.Path = SOURCES_PATH) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    if not path.exists():
        return {}, [f"canonical source inventory missing: {path}"]
    try:
        payload = load_json(path)
    except Exception as exc:
        return {}, [f"canonical source inventory is not valid JSON: {exc}"]
    if not isinstance(payload, dict):
        return {}, ["canonical source inventory must be a JSON object"]
    sources = payload.get("canonical_sources")
    if not isinstance(sources, list):
        errors.append("canonical_sources must be a list")
        sources = []
    seen = {str(item.get("path")) for item in sources if isinstance(item, dict)}
    for required in REQUIRED_SOURCE_PATHS:
        if required not in seen:
            errors.append(f"canonical source missing from inventory: {required}")
        if not pathlib.Path(required).exists():
            errors.append(f"canonical source file missing: {required}")
    rule = str(payload.get("new_work_rule", ""))
    if "Outstanding Work Register" not in rule and "outstanding" not in rule.lower():
        errors.append("new_work_rule must reference the Outstanding Work Register")
    return payload, errors


def validate_outstanding_register(path: pathlib.Path = OUTSTANDING_REGISTER_PATH) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"outstanding work register missing: {path}"]
    text = path.read_text(encoding="utf-8")
    for rr_id in REQUIRED_RR_IDS:
        if rr_id not in text:
            errors.append(f"outstanding work register missing ID: {rr_id}")
    for marker in (
        "Anti-scope-creep rule",
        "The next implementation slice must cite",
        "Privacy / POPIA completion",
        "Security posture deepening",
        "Operational drills",
        "Beta outcome reporting",
    ):
        if marker not in text:
            errors.append(f"outstanding work register missing marker: {marker}")
    return errors


def validate_classification(path: pathlib.Path = CLASSIFICATION_PATH) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"Phase 18-21 classification missing: {path}"]
    text = path.read_text(encoding="utf-8")
    for marker in (
        "auxiliary beta-operations governance",
        "not canonical roadmap phases",
        "automatic Phase 22+ creation",
        "Phase 18",
        "Phase 19",
        "Phase 20",
        "Phase 21",
    ):
        if marker not in text:
            errors.append(f"classification document missing marker: {marker}")
    return errors


def validate_freeze(path: pathlib.Path = FREEZE_PATH) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"new-work freeze document missing: {path}"]
    text = path.read_text(encoding="utf-8")
    for marker in (
        "must not introduce new roadmap phases",
        "RR-###",
        "runtime KG implementation",
        "production release",
        "public beta",
    ):
        if marker not in text:
            errors.append(f"new-work freeze missing marker: {marker}")
    return errors


def _raw_json(evidence_dir: pathlib.Path, rel: str, errors: list[str]) -> dict[str, Any]:
    path = evidence_dir / rel
    if not path.exists():
        errors.append(f"required evidence file missing: {path}")
        return {}
    try:
        payload = load_json(path)
    except Exception as exc:
        errors.append(f"invalid JSON evidence file {path}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"evidence file must contain an object: {path}")
        return {}
    return payload


def verify_record(record_path: pathlib.Path = RECORD_PATH) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not record_path.exists():
        errors.append(f"record missing: {record_path}")
        return {"valid": False, "errors": errors, "warnings": warnings}
    try:
        record = load_json(record_path)
    except Exception as exc:
        errors.append(f"record is not valid JSON: {exc}")
        return {"valid": False, "errors": errors, "warnings": warnings}
    if not isinstance(record, dict):
        errors.append("record must be a JSON object")
        return {"valid": False, "errors": errors, "warnings": warnings}

    if record.get("status") != "roadmap_reconciliation_recorded":
        errors.append("record status must be roadmap_reconciliation_recorded")
    for field in REQUIRED_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field} must be true")
    for field in REQUIRED_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field} must be false")
    if record.get("errors"):
        errors.append(f"record contains errors: {record.get('errors')}")

    _, source_errors = validate_sources_file()
    errors.extend(source_errors)
    errors.extend(validate_outstanding_register())
    errors.extend(validate_classification())
    errors.extend(validate_freeze())

    evidence_dir = pathlib.Path(str(record.get("evidence_dir", "")))
    if not evidence_dir.exists():
        errors.append(f"evidence directory missing: {evidence_dir}")
    else:
        index = evidence_dir / "evidence_index.md"
        if not index.exists():
            errors.append(f"evidence index missing: {index}")
        else:
            index_text = index.read_text(encoding="utf-8")
            for marker in (
                "Roadmap reconciliation recorded: true",
                "Canonical sources valid: true",
                "Outstanding work register valid: true",
                "Phase 18-21 classified as auxiliary governance: true",
                "New work freeze active: true",
                "Production release authorised: false",
                "Public beta authorised: false",
                "Runtime KG implementation claimed: false",
            ):
                if marker not in index_text:
                    errors.append(f"evidence index missing marker: {marker}")
        errors.extend(verify_sha256sums(evidence_dir / "SHA256SUMS.txt"))
        for rel in REQUIRED_RAW_FILES:
            if rel.endswith(".md"):
                if not (evidence_dir / rel).exists():
                    errors.append(f"required evidence file missing: {evidence_dir / rel}")
            else:
                _raw_json(evidence_dir, rel, errors)
        snapshot = _raw_json(evidence_dir, "raw/roadmap_reconciliation_record_snapshot.json", errors)
        if snapshot and snapshot != record:
            errors.append("record snapshot does not match record")
        result = _raw_json(evidence_dir, "raw/roadmap_reconciliation_result.json", errors)
        if result and result.get("valid") is not True:
            errors.append("raw roadmap reconciliation result must be valid")

    return {"valid": not errors, "errors": errors, "warnings": warnings, "record": record}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=pathlib.Path, default=RECORD_PATH)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = verify_record(args.record)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["errors"]:
        print("\n".join(result["errors"]))
    else:
        print("Roadmap reconciliation evidence is valid")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
