#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs/release/branch_protection_evidence.md"
JSON_OUT = ROOT / "docs/release/branch_protection_evidence.json"


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "enabled", "required"}


def main() -> int:
    protected_branch = os.getenv("PROTECTED_BRANCH", "codex/production_readiness").strip()
    required_checks = [item.strip() for item in os.getenv("BRANCH_REQUIRED_CHECKS", "").split(",") if item.strip()]
    pr_required = truthy(os.getenv("BRANCH_PR_REQUIRED", ""))
    admin_enforced = truthy(os.getenv("BRANCH_ADMIN_ENFORCED", ""))
    bypass_disabled = truthy(os.getenv("BRANCH_BYPASS_DISABLED", ""))
    evidence_url = os.getenv("BRANCH_PROTECTION_EVIDENCE_URL", "").strip()

    complete = bool(protected_branch and required_checks and pr_required and bypass_disabled)
    payload = {
        "status": "verified" if complete else "pending_branch_protection_evidence",
        "protected_branch": protected_branch,
        "required_checks": required_checks,
        "pull_request_required": pr_required,
        "admin_enforced": admin_enforced,
        "bypass_disabled": bypass_disabled,
        "evidence_url": evidence_url,
        "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "required": True,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    MD.write_text("\n".join([
        "# Branch Protection Evidence", "", f"**Status:** {payload['status']}", "",
        "| Field | Value |", "|---|---|",
        f"| Protected branch | {protected_branch or 'PENDING'} |",
        f"| Required checks | {', '.join(required_checks) if required_checks else 'PENDING'} |",
        f"| Pull request required | {pr_required} |",
        f"| Admin enforced | {admin_enforced} |",
        f"| Bypass disabled | {bypass_disabled} |",
        f"| Evidence URL/path | {evidence_url or 'PENDING'} |",
        f"| Captured at | {payload['captured_at']} |", "",
        "## Usage", "", "```bash",
        "PROTECTED_BRANCH=codex/production_readiness \\",
        "BRANCH_REQUIRED_CHECKS='ci-core,backend-runtime-enablement-full-check' \\",
        "BRANCH_PR_REQUIRED=true \\",
        "BRANCH_BYPASS_DISABLED=true \\",
        "make branch-protection-evidence-capture", "```", "",
    ]), encoding="utf-8")
    print(f"Wrote {MD.relative_to(ROOT)}")
    print(f"Wrote {JSON_OUT.relative_to(ROOT)}")
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
