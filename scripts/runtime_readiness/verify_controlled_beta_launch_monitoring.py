#!/usr/bin/env python3
"""Verify Phase 21 controlled beta launch-monitoring authority evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any

RECORD_PATH = pathlib.Path("docs/roadmap/execution/runtime_readiness/phase_21_controlled_beta_launch_monitoring_record.json")
FALSE_BOUNDARY_FIELDS: tuple[str, ...] = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
)
REQUIRED_TRUE_FIELDS: tuple[str, ...] = (
    "controlled_beta_launch_monitoring_claimed",
    "controlled_beta_launch_monitoring_recorded",
    "phase_20_controlled_beta_launch_activation_valid",
    "monitoring_documents_valid",
    "controlled_beta_launch_authorised",
    "live_learner_traffic_authorised",
    "learner_data_migration_authorised",
    "live_learner_traffic_observed",
    "controlled_beta_continuation_authorised",
)
REQUIRED_FALSE_FIELDS: tuple[str, ...] = (
    "critical_incidents_open",
    "rollback_required",
)
REQUIRED_RAW_FILES: tuple[str, ...] = (
    "raw/git_state.json",
    "raw/phase20_launch_activation_verification.json",
    "raw/monitoring_documents.json",
    "raw/controlled_beta_launch_monitoring_result.json",
    "raw/controlled_beta_launch_monitoring_record_snapshot.json",
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

    if record.get("status") != "controlled_beta_launch_monitoring_recorded":
        errors.append("record status must be controlled_beta_launch_monitoring_recorded")

    for field in REQUIRED_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field} must be true")

    for field in FALSE_BOUNDARY_FIELDS + REQUIRED_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field} must be false")

    if record.get("errors"):
        errors.append(f"record contains errors: {record.get('errors')}")

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
                "Controlled beta launch monitoring recorded: true",
                "Phase 20 launch activation valid: true",
                "Monitoring documents valid: true",
                "Live learner traffic observed: true",
                "Controlled beta continuation authorised: true",
                "Production release authorised: false",
                "Public beta authorised: false",
            ):
                if marker not in index_text:
                    errors.append(f"evidence index missing marker: {marker}")

        errors.extend(verify_sha256sums(evidence_dir / "SHA256SUMS.txt"))

        for rel in REQUIRED_RAW_FILES:
            _raw_json(evidence_dir, rel, errors)

        phase20 = _raw_json(evidence_dir, "raw/phase20_launch_activation_verification.json", errors)
        if phase20 and phase20.get("valid") is not True:
            errors.append("raw Phase 20 launch activation verification must be valid")

        docs = _raw_json(evidence_dir, "raw/monitoring_documents.json", errors)
        if docs and docs.get("valid") is not True:
            errors.append("raw monitoring document validation must be valid")

        snapshot = _raw_json(evidence_dir, "raw/controlled_beta_launch_monitoring_record_snapshot.json", errors)
        if snapshot and snapshot != record:
            errors.append("record snapshot does not match record")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "record": record,
    }


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
        print("Phase 21 controlled beta launch monitoring evidence is valid")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
