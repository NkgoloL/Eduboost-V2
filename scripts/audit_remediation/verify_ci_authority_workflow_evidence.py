#!/usr/bin/env python3
"""Verify TA Phase 04 CI authority workflow-cleanup evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Finding:
    valid: bool
    message: str


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: Path) -> tuple[object | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, str(exc)


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
        if rel == "ci_authority_workflow_evidence_check.json":
            findings.append(Finding(False, "ci_authority_workflow_evidence_check.json must not be self-hashed"))
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
    verification_path = raw_dir / "ci_authority_workflow_verification.json"
    findings: list[Finding] = [
        Finding(evidence_dir.exists(), "evidence directory exists" if evidence_dir.exists() else "evidence directory missing"),
        Finding(raw_dir.exists(), "raw directory exists" if raw_dir.exists() else "raw directory missing"),
        Finding((evidence_dir / "evidence_index.md").exists(), "evidence index exists" if (evidence_dir / "evidence_index.md").exists() else "evidence index missing"),
        Finding(verification_path.exists(), "workflow verification JSON exists" if verification_path.exists() else "workflow verification JSON missing"),
    ]
    payload: object | None = None
    if verification_path.exists():
        payload, error = _load_json(verification_path)
        findings.append(Finding(error is None, "workflow verification JSON is valid" if error is None else f"workflow verification JSON invalid: {error}"))
    if isinstance(payload, dict):
        findings.append(Finding(payload.get("valid") is True, "workflow verification valid=true" if payload.get("valid") is True else "workflow verification valid is not true"))
        messages = "\n".join(str(f.get("message", "")) for f in payload.get("findings", []) if isinstance(f, dict))
        for required in (
            "workflow job ids are unique",
            "required snippet present: actions/upload-artifact@v4",
            "required snippet present: pnpm --dir app/frontend install --frozen-lockfile",
            "required snippet present: pnpm exec playwright test",
            "TA-CI-001 blocker registered",
        ):
            findings.append(Finding(required in messages, f"evidence contains {required}" if required in messages else f"evidence missing {required}"))
    if raw_dir.exists():
        findings.extend(_verify_sha_manifest(raw_dir))
    return {"valid": all(f.valid for f in findings), "findings": [asdict(f) for f in findings]}


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
