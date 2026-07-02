#!/usr/bin/env python3
"""Verify TA Phase 05 dependency-scan enforcement evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE_DIR = REPO_ROOT / "docs" / "release-evidence" / "technical-audit" / "dependency-scan-enforcement"

@dataclass(frozen=True)
class Finding:
    valid: bool
    message: str


def _load_json(path: Path) -> tuple[dict[str, object] | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, str(exc)


def _verify_sha_manifest(raw: Path) -> list[Finding]:
    findings: list[Finding] = []
    manifest = raw / "SHA256SUMS.txt"
    if not manifest.exists():
        return [Finding(False, "raw/SHA256SUMS.txt missing")]
    lines = [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    findings.append(Finding(bool(lines), "SHA256SUMS.txt has entries" if lines else "SHA256SUMS.txt is empty"))
    for line in lines:
        try:
            digest, filename = line.split(None, 1)
        except ValueError:
            findings.append(Finding(False, f"invalid SHA256SUMS line: {line}"))
            continue
        filename = filename.strip()
        if filename in {"SHA256SUMS.txt", "dependency_scan_evidence_check.json"}:
            findings.append(Finding(False, f"{filename} must not be self-hashed"))
            continue
        target = raw / filename
        if not target.exists():
            findings.append(Finding(False, f"raw/{filename} missing"))
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        findings.append(Finding(actual == digest, f"raw/{filename} digest matches" if actual == digest else f"raw/SHA256SUMS.txt digest mismatch for {filename}"))
    return findings


def verify(evidence_dir: Path = DEFAULT_EVIDENCE_DIR) -> dict[str, object]:
    raw = evidence_dir / "raw"
    findings: list[Finding] = []
    findings.append(Finding(evidence_dir.exists(), "evidence directory exists" if evidence_dir.exists() else "evidence directory missing"))
    findings.append(Finding((evidence_dir / "evidence_index.md").exists(), "evidence index exists" if (evidence_dir / "evidence_index.md").exists() else "evidence index missing"))
    findings.append(Finding(raw.exists(), "raw evidence directory exists" if raw.exists() else "raw evidence directory missing"))
    verification_path = raw / "dependency_scan_enforcement_verification.json"
    verification, error = _load_json(verification_path)
    findings.append(Finding(error is None, "dependency scan verification JSON is readable" if error is None else f"dependency scan verification JSON invalid: {error}"))
    if isinstance(verification, dict):
        findings.append(Finding(verification.get("valid") is True, "dependency scan verifier returned valid true" if verification.get("valid") is True else "dependency scan verifier did not return valid true"))
        messages = "\n".join(str(item.get("message", "")) for item in verification.get("findings", []) if isinstance(item, dict))
        for message in ("pip-audit uses fail-closed shell options", "pnpm-audit uses fail-closed shell options", "pnpm critical vulnerabilities fail the job", "all dependency scan artifact uploads use v4", "TA-SECURITY-001 blocker registered"):
            findings.append(Finding(message in messages, f"verification proves: {message}" if message in messages else f"verification missing proof: {message}"))
    workflow_snapshot = raw / "dependency-scan.yml.snapshot"
    findings.append(Finding(workflow_snapshot.exists(), "workflow snapshot captured" if workflow_snapshot.exists() else "workflow snapshot missing"))
    if workflow_snapshot.exists():
        text = workflow_snapshot.read_text(encoding="utf-8")
        findings.append(Finding("|| true" not in text, "workflow snapshot has no broad audit suppression" if "|| true" not in text else "workflow snapshot still contains || true"))
        findings.append(Finding("actions/upload-artifact@v7" not in text, "workflow snapshot has no unsupported upload-artifact@v7" if "actions/upload-artifact@v7" not in text else "workflow snapshot still contains upload-artifact@v7"))
    if raw.exists():
        findings.extend(_verify_sha_manifest(raw))
    return {"valid": all(f.valid for f in findings), "evidence_dir": str(evidence_dir), "findings": [asdict(f) for f in findings], "remote_scan_run_claimed": False}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
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
