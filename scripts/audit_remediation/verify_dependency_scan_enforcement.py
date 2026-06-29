#!/usr/bin/env python3
"""Verify TA Phase 05 dependency-scan enforcement contract.

This is a static workflow-authority verifier. It proves that the dependency
scan workflow is configured to fail on configured severity and publish evidence
artifacts consistently. It does not claim that GitHub-hosted scans have run.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "dependency-scan.yml"
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


def _section(text: str, job_id: str) -> str:
    pattern = re.compile(rf"^  {re.escape(job_id)}:\s*$", re.M)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.start()
    next_match = re.search(r"^  [A-Za-z0-9_-]+:\s*$", text[match.end():], re.M)
    end = match.end() + next_match.start() if next_match else len(text)
    return text[start:end]


def verify() -> dict[str, object]:
    text = _read(WORKFLOW)
    findings: list[Finding] = []
    findings.append(Finding(WORKFLOW.exists(), "dependency-scan workflow exists" if WORKFLOW.exists() else "dependency-scan workflow missing"))
    jobs = _job_ids(text)
    duplicates = sorted({job for job in jobs if jobs.count(job) > 1})
    findings.append(Finding(not duplicates, "dependency-scan job ids are unique" if not duplicates else f"duplicate dependency-scan job ids: {duplicates}"))
    for job in ("pip-audit", "pnpm-audit", "dependency-review", "summary"):
        findings.append(Finding(job in jobs, f"job {job} present" if job in jobs else f"job {job} missing"))

    for snippet in ("|| true", "actions/upload-artifact@v7", "steps.publish.outputs.result_url", "needs.npm-audit"):
        findings.append(Finding(snippet not in text, f"forbidden snippet absent: {snippet}" if snippet not in text else f"forbidden snippet present: {snippet}"))

    for snippet in (
        "security-events: write",
        "actions/upload-artifact@v4",
        "uses: pnpm/action-setup@v4",
        "cache: 'pnpm'",
        "cache-dependency-path: app/frontend/pnpm-lock.yaml",
        "fail-on-severity: critical",
        "needs.pnpm-audit.result",
    ):
        findings.append(Finding(snippet in text, f"required snippet present: {snippet}" if snippet in text else f"required snippet missing: {snippet}"))

    pip = _section(text, "pip-audit")
    findings.append(Finding("set -euo pipefail" in pip, "pip-audit uses fail-closed shell options" if "set -euo pipefail" in pip else "pip-audit must use set -euo pipefail"))
    findings.append(Finding("pip-audit -r ${{ matrix.requirements }} --format=json" in pip, "pip-audit scans requirements matrix" if "pip-audit -r ${{ matrix.requirements }} --format=json" in pip else "pip-audit requirements matrix scan missing"))
    findings.append(Finding("tee pip-audit.json" in pip, "pip-audit JSON artifact is captured" if "tee pip-audit.json" in pip else "pip-audit JSON artifact not captured"))
    findings.append(Finding("requirements/base.txt" in pip and "requirements/dev.txt" in pip and "requirements/docs.txt" in pip and "requirements-ml.txt" in pip, "pip-audit matrix covers tracked requirement sets" if "requirements/base.txt" in pip and "requirements/dev.txt" in pip and "requirements/docs.txt" in pip and "requirements-ml.txt" in pip else "pip-audit matrix must cover tracked requirement sets"))

    pnpm = _section(text, "pnpm-audit")
    findings.append(Finding("set -euo pipefail" in pnpm, "pnpm-audit uses fail-closed shell options" if "set -euo pipefail" in pnpm else "pnpm-audit must use set -euo pipefail"))
    findings.append(Finding("pnpm audit --audit-level=critical --json" in pnpm, "pnpm audit uses critical threshold" if "pnpm audit --audit-level=critical --json" in pnpm else "pnpm audit critical threshold missing"))
    findings.append(Finding("tee pnpm-audit.json" in pnpm, "pnpm audit JSON artifact is captured" if "tee pnpm-audit.json" in pnpm else "pnpm audit JSON artifact not captured"))
    findings.append(Finding("critical > 0" in pnpm and "process.exitCode = 1" in pnpm, "pnpm critical vulnerabilities fail the job" if "critical > 0" in pnpm and "process.exitCode = 1" in pnpm else "pnpm critical vulnerability failure guard missing"))
    findings.append(Finding("pnpm install --frozen-lockfile" in pnpm, "pnpm audit installs from frozen lockfile" if "pnpm install --frozen-lockfile" in pnpm else "pnpm audit must use frozen lockfile"))

    uploads = [line.strip() for line in text.splitlines() if "uses: actions/upload-artifact" in line]
    findings.append(Finding(bool(uploads), "dependency scan uploads audit artifacts" if uploads else "dependency scan artifact uploads missing"))
    findings.append(Finding(all(line.endswith("@v4") for line in uploads), "all dependency scan artifact uploads use v4" if uploads and all(line.endswith("@v4") for line in uploads) else f"artifact uploads must use v4: {uploads}"))

    if BLOCKER_REGISTER.exists():
        try:
            data = json.loads(BLOCKER_REGISTER.read_text(encoding="utf-8"))
            blockers = data.get("remaining_release_blockers_after_reset", [])
            security = next((item for item in blockers if item.get("id") == "TA-SECURITY-001"), None)
            findings.append(Finding(isinstance(security, dict), "TA-SECURITY-001 blocker registered" if isinstance(security, dict) else "TA-SECURITY-001 blocker missing"))
            if isinstance(security, dict):
                findings.append(Finding(security.get("status") in {"dependency_scan_enforcement_ready", "evidence_recorded", "partially_addressed_in_baseline_reset"}, f"TA-SECURITY-001 status {security.get('status')}"))
            allowed_active_slices = {
                "05-dependency-scan-enforcement",
                    "next-technical-audit-slice",
                    "04-ci-authority-workflow-cleanup",
                    "technical-audit-remediation-closed",
            }
            terminal_closed = data.get("status") == "phase_12_technical_audit_remediation_closed"
            findings.append(Finding(data.get("active_slice") in allowed_active_slices or terminal_closed, f"active_slice is {data.get('active_slice')}"))
        except Exception as exc:
            findings.append(Finding(False, f"blocker register invalid JSON: {exc}"))
    else:
        findings.append(Finding(False, "blocker register missing"))

    return {"valid": all(f.valid for f in findings), "workflow": str(WORKFLOW.relative_to(REPO_ROOT)), "job_ids": jobs, "findings": [asdict(f) for f in findings], "remote_scan_run_claimed": False}


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
