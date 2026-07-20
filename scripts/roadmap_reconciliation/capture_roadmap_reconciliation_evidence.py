#!/usr/bin/env python3
"""Capture evidence for the Roadmap Reconciliation Slice."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import sys
from scripts._subprocess import run
from datetime import datetime, timezone
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from scripts.roadmap_reconciliation.verify_roadmap_reconciliation import (
    CLASSIFICATION_PATH,
    FREEZE_PATH,
    OUTSTANDING_REGISTER_PATH,
    RECORD_PATH,
    REQUIRED_FALSE_FIELDS,
    SOURCES_PATH,
    validate_classification,
    validate_freeze,
    validate_outstanding_register,
    validate_sources_file,
)

EVIDENCE_DIR = pathlib.Path("docs/release-evidence/roadmap-reconciliation/roadmap-reconciliation-slice")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_state(target_branch: str) -> dict[str, Any]:
    def _git(*args: str) -> str:
        proc = run(["git", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        return proc.stdout.strip()
    return {
        "branch": _git("branch", "--show-current"),
        "head_sha": _git("rev-parse", "HEAD"),
        "target_branch": target_branch,
        "target_sha": _git("rev-parse", target_branch) or _git("rev-parse", f"origin/{target_branch}"),
        "status_short": _git("status", "--short"),
    }


def validate_all() -> dict[str, Any]:
    errors: list[str] = []
    source_payload, source_errors = validate_sources_file(SOURCES_PATH)
    errors.extend(source_errors)
    errors.extend(validate_outstanding_register(OUTSTANDING_REGISTER_PATH))
    errors.extend(validate_classification(CLASSIFICATION_PATH))
    errors.extend(validate_freeze(FREEZE_PATH))
    source_hashes: dict[str, str] = {}
    for item in source_payload.get("canonical_sources", []) if isinstance(source_payload, dict) else []:
        if isinstance(item, dict) and item.get("path"):
            path = pathlib.Path(str(item["path"]))
            if path.exists():
                source_hashes[str(path)] = sha256_file(path)
    for path in (SOURCES_PATH, OUTSTANDING_REGISTER_PATH, CLASSIFICATION_PATH, FREEZE_PATH):
        if path.exists():
            source_hashes[str(path)] = sha256_file(path)
    return {
        "valid": not errors,
        "errors": errors,
        "canonical_sources_valid": not source_errors,
        "outstanding_work_register_valid": not validate_outstanding_register(OUTSTANDING_REGISTER_PATH),
        "phase_18_to_21_classified_as_auxiliary_governance": not validate_classification(CLASSIFICATION_PATH),
        "new_work_freeze_active": not validate_freeze(FREEZE_PATH),
        "source_hashes": source_hashes,
    }


def write_evidence_index(evidence_dir: pathlib.Path, record: dict[str, Any]) -> None:
    text = f"""# Roadmap Reconciliation Evidence Index

Captured at: `{record['captured_at']}`  
Owner: `{record['reconciliation_owner']}`  
Status: `{record['status']}`

## Result

- Roadmap reconciliation recorded: {str(record['roadmap_reconciliation_recorded']).lower()}
- Canonical sources valid: {str(record['canonical_sources_valid']).lower()}
- Outstanding work register valid: {str(record['outstanding_work_register_valid']).lower()}
- Phase 18-21 classified as auxiliary governance: {str(record['phase_18_to_21_classified_as_auxiliary_governance']).lower()}
- New work freeze active: {str(record['new_work_freeze_active']).lower()}
- Next work must cite outstanding work register: {str(record['next_work_must_cite_outstanding_work_register']).lower()}

## Boundary

- Production release authorised: {str(record['production_release_authorised']).lower()}
- Deployment authorised: {str(record['deployment_authorised']).lower()}
- Release tag authorised: {str(record['release_tag_authorised']).lower()}
- Public beta authorised: {str(record['public_beta_authorised']).lower()}
- New unreconciled work authorised: {str(record['new_unreconciled_work_authorised']).lower()}
- Runtime KG implementation claimed: {str(record['runtime_kg_implementation_claimed']).lower()}

## Raw evidence

- `raw/git_state.json`
- `raw/canonical_roadmap_sources_snapshot.json`
- `raw/source_hashes.json`
- `raw/outstanding_work_register_snapshot.md`
- `raw/phase_18_to_21_governance_classification_snapshot.md`
- `raw/roadmap_new_work_freeze_snapshot.md`
- `raw/roadmap_reconciliation_result.json`
- `raw/roadmap_reconciliation_record_snapshot.json`
"""
    (evidence_dir / "evidence_index.md").write_text(text, encoding="utf-8")


def write_sha256sums(evidence_dir: pathlib.Path) -> None:
    files = sorted(p for p in evidence_dir.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt")
    lines = [f"{sha256_file(path)}  {path.as_posix()}" for path in files]
    (evidence_dir / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim-roadmap-reconciliation", action="store_true")
    parser.add_argument("--reconciliation-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--evidence-dir", type=pathlib.Path, default=EVIDENCE_DIR)
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evidence_dir = args.evidence_dir
    raw_dir = evidence_dir / "raw"
    if evidence_dir.exists():
        shutil.rmtree(evidence_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    result = validate_all()
    claimed = bool(args.claim_roadmap_reconciliation)
    valid = bool(claimed and result["valid"])
    errors = [] if valid else list(result["errors"])
    if not claimed:
        errors.append("--claim-roadmap-reconciliation was not supplied")

    record = {
        "version": 1,
        "status": "roadmap_reconciliation_recorded" if valid else "roadmap_reconciliation_capture_invalid",
        "captured_at": utc_now(),
        "reconciliation_owner": args.reconciliation_owner,
        "target_branch": args.target_branch,
        "roadmap_reconciliation_claimed": claimed,
        "roadmap_reconciliation_recorded": valid,
        "canonical_sources_valid": bool(result["canonical_sources_valid"]),
        "outstanding_work_register_valid": bool(result["outstanding_work_register_valid"]),
        "phase_18_to_21_classified_as_auxiliary_governance": bool(result["phase_18_to_21_classified_as_auxiliary_governance"]),
        "new_work_freeze_active": bool(result["new_work_freeze_active"]),
        "next_work_must_cite_outstanding_work_register": True,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "new_unreconciled_work_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "evidence_dir": evidence_dir.as_posix(),
        "errors": errors,
    }

    write_json(raw_dir / "git_state.json", git_state(args.target_branch))
    write_json(raw_dir / "canonical_roadmap_sources_snapshot.json", load_json(SOURCES_PATH))
    write_json(raw_dir / "source_hashes.json", result["source_hashes"])
    (raw_dir / "outstanding_work_register_snapshot.md").write_text(OUTSTANDING_REGISTER_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    (raw_dir / "phase_18_to_21_governance_classification_snapshot.md").write_text(CLASSIFICATION_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    (raw_dir / "roadmap_new_work_freeze_snapshot.md").write_text(FREEZE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    write_json(raw_dir / "roadmap_reconciliation_result.json", {"valid": valid, "errors": errors, **result})
    write_json(raw_dir / "roadmap_reconciliation_record_snapshot.json", record)
    write_evidence_index(evidence_dir, record)
    write_sha256sums(evidence_dir)
    write_json(RECORD_PATH, record)

    output = {"valid": valid, "errors": errors, "record": record}
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    elif errors:
        print("\n".join(errors))
    else:
        print("Roadmap reconciliation evidence captured")
    if args.require_valid and not valid:
        return 1
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
