#!/usr/bin/env python3
"""Verify TA Phase 04 CI authority workflow cleanup.

This verifier is intentionally static. It proves the repository workflow contract
is structurally consistent; it does not claim that GitHub-hosted CI has run.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_CD = REPO_ROOT / ".github" / "workflows" / "ci-cd.yml"
FRONTEND_LOCKFILE = REPO_ROOT / "app" / "frontend" / "pnpm-lock.yaml"
ROOT_PACKAGE = REPO_ROOT / "package.json"
FRONTEND_PACKAGE = REPO_ROOT / "app" / "frontend" / "package.json"
BLOCKER_REGISTER = REPO_ROOT / "docs" / "roadmap" / "execution" / "technical_audit_remediation" / "blocker_register.json"


@dataclass(frozen=True)
class Finding:
    valid: bool
    message: str


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _job_ids(workflow_text: str) -> list[str]:
    in_jobs = False
    ids: list[str] = []
    for line in workflow_text.splitlines():
        if line.startswith("jobs:"):
            in_jobs = True
            continue
        if in_jobs:
            match = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
            if match:
                ids.append(match.group(1))
    return ids


def _needs_line(workflow_text: str) -> str:
    for line in workflow_text.splitlines():
        if line.strip().startswith("needs:") and "production-promote" not in line:
            stripped = line.strip()
            if "content-factory-migrations" in stripped and "schema-drift" in stripped:
                return stripped
    return ""


def verify() -> dict[str, object]:
    text = _read(CI_CD)
    findings: list[Finding] = []

    findings.append(Finding(CI_CD.exists(), ".github/workflows/ci-cd.yml exists" if CI_CD.exists() else ".github/workflows/ci-cd.yml missing"))
    findings.append(Finding(FRONTEND_LOCKFILE.exists(), "frontend pnpm-lock.yaml exists" if FRONTEND_LOCKFILE.exists() else "frontend pnpm-lock.yaml missing"))

    if ROOT_PACKAGE.exists():
        root_package = _read(ROOT_PACKAGE)
        findings.append(Finding('"packageManager": "pnpm@' in root_package, "root packageManager uses pnpm" if '"packageManager": "pnpm@' in root_package else "root packageManager must use pnpm"))
    else:
        findings.append(Finding(False, "root package.json missing"))

    if FRONTEND_PACKAGE.exists():
        frontend_package = _read(FRONTEND_PACKAGE)
        findings.append(Finding('"packageManager": "pnpm@' in frontend_package, "frontend packageManager uses pnpm" if '"packageManager": "pnpm@' in frontend_package else "frontend packageManager must use pnpm"))
    else:
        findings.append(Finding(False, "frontend package.json missing"))

    jobs = _job_ids(text)
    duplicates = sorted({job for job in jobs if jobs.count(job) > 1})
    findings.append(Finding(not duplicates, "workflow job ids are unique" if not duplicates else f"duplicate workflow job ids: {duplicates}"))
    for required in ("schema-drift", "alembic-drift", "frontend", "e2e", "production-promote"):
        findings.append(Finding(required in jobs, f"job {required} present" if required in jobs else f"job {required} missing"))

    forbidden = (
        "npm ci",
        "package-lock.json",
        "app/frontend/node_modules/.bin/playwright",
        "actions/upload-artifact@v7",
        "actions/setup-node@v6",
        "actions/setup-python@v6",
    )
    for snippet in forbidden:
        findings.append(Finding(snippet not in text, f"forbidden snippet absent: {snippet}" if snippet not in text else f"forbidden snippet present: {snippet}"))

    required_snippets = (
        "actions/upload-artifact@v4",
        "pnpm/action-setup@v4",
        "cache: \"pnpm\"",
        "app/frontend/pnpm-lock.yaml",
        "pnpm install --frozen-lockfile",
        "pnpm --dir app/frontend install --frozen-lockfile",
        "pnpm run env-check",
        "pnpm run lint",
        "pnpm run type-check",
        "pnpm run build",
        "pnpm exec playwright install --with-deps chromium",
        "pnpm exec playwright test",
    )
    for snippet in required_snippets:
        findings.append(Finding(snippet in text, f"required snippet present: {snippet}" if snippet in text else f"required snippet missing: {snippet}"))

    needs = _needs_line(text)
    for required_need in ("schema-drift", "alembic-drift", "frontend", "e2e", "unit-tests", "integration-tests"):
        findings.append(Finding(required_need in needs, f"production-promote needs {required_need}" if required_need in needs else f"production-promote missing need {required_need}"))

    if BLOCKER_REGISTER.exists():
        try:
            data = json.loads(BLOCKER_REGISTER.read_text(encoding="utf-8"))
            blockers = data.get("remaining_release_blockers_after_reset", [])
            ci = next((item for item in blockers if item.get("id") == "TA-CI-001"), None)
            findings.append(Finding(ci is not None, "TA-CI-001 blocker registered" if ci else "TA-CI-001 blocker missing"))
            if isinstance(ci, dict):
                findings.append(Finding(ci.get("status") in {"workflow_cleanup_ready", "evidence_recorded"}, f"TA-CI-001 status {ci.get('status')}"))
            allowed_active_slices = {
                "04-ci-authority-workflow-cleanup",
                    "next-technical-audit-slice",
                    "technical-audit-remediation-closed",
            }
            terminal_closed = data.get("status") == "phase_12_technical_audit_remediation_closed"
            findings.append(Finding(data.get("active_slice") in allowed_active_slices or terminal_closed, f"active_slice is {data.get('active_slice')}"))
        except Exception as exc:
            findings.append(Finding(False, f"blocker register invalid JSON: {exc}"))
    else:
        findings.append(Finding(False, "blocker register missing"))

    return {
        "valid": all(f.valid for f in findings),
        "workflow": str(CI_CD.relative_to(REPO_ROOT)),
        "job_ids": jobs,
        "findings": [asdict(f) for f in findings],
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = verify()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for finding in payload["findings"]:
            print(f"{'PASS' if finding['valid'] else 'FAIL'} {finding['message']}")
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
