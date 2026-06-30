#!/usr/bin/env python3
"""Verify Phase 03 frontend/tooling authority evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

EXPECTED_STEPS = (
    "pnpm_version",
    "pnpm_install_frozen_lockfile",
    "frontend_env_check",
    "frontend_type_check",
    "frontend_lint",
    "frontend_vitest",
)


@dataclass(frozen=True)
class Finding:
    valid: bool
    message: str


def _load_json(path: Path) -> tuple[object | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, str(exc)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _verify_sha_manifest(raw_dir: Path) -> list[Finding]:
    manifest = raw_dir / "SHA256SUMS.txt"
    findings: list[Finding] = []
    if not manifest.exists():
        return [Finding(False, "raw/SHA256SUMS.txt missing")]
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, rel = line.split(maxsplit=1)
        except ValueError:
            findings.append(Finding(False, f"malformed SHA256SUMS line: {line!r}"))
            continue
        rel = rel.strip().lstrip("*")
        if rel == "SHA256SUMS.txt":
            findings.append(Finding(False, "SHA256SUMS.txt must not include itself"))
            continue
        target = raw_dir / rel
        if not target.exists():
            findings.append(Finding(False, f"raw/SHA256SUMS.txt references missing file {rel}"))
            continue
        actual = _sha256(target)
        findings.append(Finding(actual == expected, f"raw/SHA256SUMS.txt {'matches' if actual == expected else 'digest mismatch for'} {rel}"))
    return findings


def verify(evidence_dir: Path) -> dict[str, object]:
    raw_dir = evidence_dir / "raw"
    result_path = raw_dir / "frontend_tooling_authority_result.json"
    findings: list[Finding] = [
        Finding(evidence_dir.exists(), "evidence directory exists" if evidence_dir.exists() else "evidence directory missing"),
        Finding(raw_dir.exists(), "raw directory exists" if raw_dir.exists() else "raw directory missing"),
        Finding((evidence_dir / "evidence_index.md").exists(), "evidence index exists" if (evidence_dir / "evidence_index.md").exists() else "evidence index missing"),
        Finding(result_path.exists(), "authority result exists" if result_path.exists() else "authority result missing"),
    ]
    result: object | None = None
    if result_path.exists():
        result, error = _load_json(result_path)
        findings.append(Finding(error is None, "authority result is valid JSON" if error is None else f"authority result invalid JSON: {error}"))
    if isinstance(result, dict):
        findings.append(Finding(result.get("valid") is True, "authority result valid=true" if result.get("valid") is True else "authority result valid is not true"))
        findings.append(Finding(result.get("diagnostic_only") is False, "authority result is not diagnostic-only" if result.get("diagnostic_only") is False else "diagnostic-only run cannot be passing evidence"))
        steps = result.get("steps")
        if isinstance(steps, list):
            by_name = {step.get("name"): step for step in steps if isinstance(step, dict)}
        else:
            by_name = {}
        for name in EXPECTED_STEPS:
            step = by_name.get(name)
            findings.append(Finding(step is not None, f"step {name} present" if step is not None else f"step {name} missing"))
            if isinstance(step, dict):
                findings.append(Finding(step.get("returncode") == 0, f"step {name} returncode 0" if step.get("returncode") == 0 else f"step {name} returncode {step.get('returncode')}"))
    if raw_dir.exists():
        findings.extend(_verify_sha_manifest(raw_dir))
    payload = {"valid": all(f.valid for f in findings), "findings": [asdict(f) for f in findings]}
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = verify(args.evidence_dir)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for finding in payload["findings"]:
            print(f"{'PASS' if finding['valid'] else 'FAIL'} {finding['message']}")
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
