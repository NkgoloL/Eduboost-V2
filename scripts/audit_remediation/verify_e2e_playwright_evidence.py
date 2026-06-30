#!/usr/bin/env python3
"""Verify TA Phase 06 Playwright/E2E authority evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE_DIR = REPO_ROOT / "docs/release-evidence/technical-audit/e2e-playwright-authority"


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


def _load_json(path: Path) -> tuple[dict[str, object] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, str(exc)
    return payload if isinstance(payload, dict) else None, None if isinstance(payload, dict) else "JSON root is not an object"


def _verify_sha_manifest(raw_dir: Path) -> list[Finding]:
    manifest = raw_dir / "SHA256SUMS.txt"
    findings: list[Finding] = []
    if not manifest.exists():
        return [Finding(False, "raw/SHA256SUMS.txt missing")]
    lines = [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    findings.append(Finding(bool(lines), "SHA256SUMS.txt has entries" if lines else "SHA256SUMS.txt is empty"))
    for line in lines:
        try:
            expected, rel = line.split(maxsplit=1)
        except ValueError:
            findings.append(Finding(False, f"malformed SHA256SUMS line: {line!r}"))
            continue
        rel = rel.strip().lstrip("*")
        if rel in {"SHA256SUMS.txt", "e2e_playwright_evidence_check.json"}:
            findings.append(Finding(False, f"{rel} must not be self-hashed"))
            continue
        target = raw_dir / rel
        if not target.exists():
            findings.append(Finding(False, f"raw/SHA256SUMS.txt references missing file {rel}"))
            continue
        actual = _sha256(target)
        findings.append(Finding(actual == expected, f"raw/{rel} digest matches" if actual == expected else f"raw/SHA256SUMS.txt digest mismatch for {rel}"))
    return findings


def verify(evidence_dir: Path = DEFAULT_EVIDENCE_DIR) -> dict[str, object]:
    raw_dir = evidence_dir / "raw"
    findings: list[Finding] = [
        Finding(evidence_dir.exists(), "evidence directory exists" if evidence_dir.exists() else "evidence directory missing"),
        Finding(raw_dir.exists(), "raw directory exists" if raw_dir.exists() else "raw directory missing"),
        Finding((evidence_dir / "evidence_index.md").exists(), "evidence index exists" if (evidence_dir / "evidence_index.md").exists() else "evidence index missing"),
    ]

    verification, verification_error = _load_json(raw_dir / "e2e_playwright_authority_verification.json")
    findings.append(Finding(verification_error is None, "static authority verification JSON is readable" if verification_error is None else f"static authority verification JSON invalid: {verification_error}"))
    if isinstance(verification, dict):
        findings.append(Finding(verification.get("valid") is True, "static authority verification returned valid true" if verification.get("valid") is True else "static authority verification did not return valid true"))

    result, result_error = _load_json(raw_dir / "e2e_playwright_authority_result.json")
    findings.append(Finding(result_error is None, "Playwright authority result JSON is readable" if result_error is None else f"Playwright authority result JSON invalid: {result_error}"))
    if isinstance(result, dict):
        findings.append(Finding(result.get("valid") is True, "Playwright authority result valid true" if result.get("valid") is True else "Playwright authority result is not valid true"))
        findings.append(Finding(result.get("remote_ci_run_claimed") is False, "remote CI run is not claimed" if result.get("remote_ci_run_claimed") is False else "remote CI run must not be claimed"))
        findings.append(Finding(result.get("full_backend_backed_e2e_claimed") is False, "full backend-backed E2E is not claimed" if result.get("full_backend_backed_e2e_claimed") is False else "full backend-backed E2E must not be claimed"))
        steps = result.get("steps", [])
        if isinstance(steps, list):
            step_names = {str(step.get("name")) for step in steps if isinstance(step, dict)}
            for required in ("pnpm_version", "root_pnpm_install", "frontend_pnpm_install", "playwright_version", "playwright_mocked_journeys"):
                findings.append(Finding(required in step_names, f"authority step recorded: {required}" if required in step_names else f"authority step missing: {required}"))
            for step in steps:
                if isinstance(step, dict):
                    findings.append(Finding(step.get("returncode") == 0, f"{step.get('name')} returned 0" if step.get("returncode") == 0 else f"{step.get('name')} returned {step.get('returncode')}"))

    for snapshot in ("ci-cd.yml.snapshot", "e2e.yml.snapshot", "frontend-e2e.yml.snapshot", "playwright.config.ts.snapshot"):
        findings.append(Finding((raw_dir / snapshot).exists(), f"{snapshot} captured" if (raw_dir / snapshot).exists() else f"{snapshot} missing"))

    if raw_dir.exists():
        findings.extend(_verify_sha_manifest(raw_dir))
    return {"valid": all(f.valid for f in findings), "evidence_dir": str(evidence_dir), "remote_ci_run_claimed": False, "full_backend_backed_e2e_claimed": False, "findings": [asdict(f) for f in findings]}


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
