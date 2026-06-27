#!/usr/bin/env python3
"""Verify backend fast-gate candidate evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE_DIR = ROOT / "docs/release-evidence/technical-audit/backend-fast-gate"


def _load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"raw/{path.name} must be valid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}")
    except OSError as exc:
        errors.append(f"raw/{path.name} could not be read: {exc}")
    return None


def _verify_sha256sums(evidence_dir: Path, raw: Path, errors: list[str], warnings: list[str]) -> None:
    sums_path = raw / "SHA256SUMS.txt"
    if not sums_path.exists():
        return
    lines = [line.strip() for line in sums_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        errors.append("raw/SHA256SUMS.txt must not be empty")
        return
    for line in lines:
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            errors.append(f"raw/SHA256SUMS.txt contains malformed line: {line!r}")
            continue
        digest, rel = parts
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"raw/SHA256SUMS.txt contains invalid digest for {rel}")
            continue
        rel = rel.lstrip("*")
        if rel.endswith("raw/SHA256SUMS.txt") or rel == "SHA256SUMS.txt":
            errors.append("raw/SHA256SUMS.txt must not include a self-referential hash")
            continue
        path = evidence_dir / rel if rel.startswith("raw/") else raw / rel
        if not path.exists():
            errors.append(f"raw/SHA256SUMS.txt references missing artifact: {rel}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"raw/SHA256SUMS.txt digest mismatch for {rel}")
    if not any("backend_fast_gate_result.json" in line for line in lines):
        warnings.append("raw/SHA256SUMS.txt does not list backend_fast_gate_result.json")


def verify(evidence_dir: Path = DEFAULT_EVIDENCE_DIR) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []
    raw = evidence_dir / "raw"

    required = [
        "phase02r_terminal_gate_control.json",
        "baseline_reset_check.json",
        "openapi_route_contract.json",
        "popia_route_contract.json",
        "frontend_env_contract.json",
        "dependency_scan_workflow.json",
        "backend_fast_preflight.json",
        "compileall.txt",
        "backend_fast_gate.txt",
        "backend_fast_gate_result.json",
        "backend_fast_runner_stdout.json",
        "backend_fast_failure_classification.json",
        "SHA256SUMS.txt",
    ]
    for name in required:
        path = raw / name
        if not path.exists():
            errors.append(f"missing raw evidence artifact: raw/{name}")
        else:
            checked.append(str(path.relative_to(evidence_dir)))

    json_validity_files = [
        "phase02r_terminal_gate_control.json",
        "baseline_reset_check.json",
        "openapi_route_contract.json",
        "popia_route_contract.json",
        "frontend_env_contract.json",
        "dependency_scan_workflow.json",
        "backend_fast_preflight.json",
    ]
    for name in json_validity_files:
        path = raw / name
        if path.exists():
            payload = _load_json(path, errors)
            if payload is not None and payload.get("valid") is not True:
                errors.append(f"raw/{name} must report valid=true")

    result_path = raw / "backend_fast_gate_result.json"
    if result_path.exists():
        result = _load_json(result_path, errors)
        if result is not None:
            if result.get("valid") is not True or result.get("returncode") != 0:
                errors.append("backend fast gate result must be valid with returncode 0")
            if result.get("command") != "make test-fast":
                errors.append("backend fast gate result must record command 'make test-fast'")

    classification_path = raw / "backend_fast_failure_classification.json"
    if classification_path.exists():
        classification = _load_json(classification_path, errors)
        if classification is not None:
            failure_count = int(classification.get("failure_count", 0) or 0)
            failed_tests = classification.get("failed_tests") or []
            category_names = classification.get("category_names") or []
            if classification.get("valid") is not True:
                errors.append("backend fast failure classification must report valid=true")
            if failure_count != 0:
                errors.append("backend fast failure classification must detect zero failures")
            if failed_tests:
                errors.append("backend fast failure classification must not list failed tests")
            if category_names and (failure_count or failed_tests):
                errors.append("backend fast failure classification must not match diagnostic categories for failed output")
            elif category_names:
                warnings.append("backend fast failure classification recorded diagnostic categories despite zero failures")

    runner_path = raw / "backend_fast_runner_stdout.json"
    if runner_path.exists():
        runner = _load_json(runner_path, errors)
        if runner is not None and (runner.get("valid") is not True or runner.get("returncode") != 0):
            errors.append("backend fast runner stdout JSON must report valid=true and returncode 0")

    gate_text_path = raw / "backend_fast_gate.txt"
    if gate_text_path.exists():
        gate_text = gate_text_path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"(^|\n)(FAILED|ERROR)\s+tests/", gate_text):
            errors.append("backend fast gate output still contains failed/error test lines")
        # Pytest summaries may legitimately include xfailed entries, e.g.
        # ``2315 passed, 11 skipped, 1 xfailed, 4 warnings``.  Treat only an
        # explicit non-zero ``failed``/``error`` count as a failed authority
        # summary; do not match the ``failed`` substring inside ``xfailed``.
        if re.search(r"(?:^|[,\s])([1-9]\d*)\s+failed(?:,|\s+in\b)", gate_text):
            errors.append("backend fast gate output still contains failure summary or make error")
        if re.search(r"(?:^|[,\s])([1-9]\d*)\s+errors?(?:,|\s+in\b)", gate_text, flags=re.IGNORECASE):
            errors.append("backend fast gate output still contains error summary or make error")
        if re.search(r"make: \*\*\* .*Error [1-9]", gate_text):
            errors.append("backend fast gate output still contains failure summary or make error")

    index_path = evidence_dir / "evidence_index.md"
    if not index_path.exists():
        errors.append("missing evidence_index.md")
    else:
        checked.append("evidence_index.md")
        index_text = index_path.read_text(encoding="utf-8")
        if "Status:** Candidate verification passed — human approval pending" not in index_text:
            errors.append("evidence index must record candidate verification passing and pending approval")
        if not re.search(r"Source commit:\*\*\s*[0-9a-f]{40}", index_text):
            errors.append("evidence index must include a 40-character source commit")
        if "does not claim full product release readiness" not in index_text:
            errors.append("evidence index must preserve release-readiness boundary")

    _verify_sha256sums(evidence_dir, raw, errors, warnings)

    return {"valid": not errors, "errors": errors, "warnings": warnings, "checked": checked}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    args = parser.parse_args()
    result = verify(args.evidence_dir.resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("BACKEND FAST EVIDENCE PASSED" if result["valid"] else "BACKEND FAST EVIDENCE FAILED")
        for error in result["errors"]:
            print(f"- {error}")
        for warning in result["warnings"]:
            print(f"warning: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
