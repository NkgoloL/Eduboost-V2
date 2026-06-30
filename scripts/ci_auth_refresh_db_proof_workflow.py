from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/auth-refresh-db-proof.yml"
STATUS_JSON = ROOT / "docs/release/ci_auth_refresh_db_proof_workflow_status.json"
STATUS_MD = ROOT / "docs/release/ci_auth_refresh_db_proof_workflow_status.md"


@dataclass(frozen=True)
class WorkflowCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class WorkflowStatus:
    generated_at: str
    current_commit: str
    status: str
    checks: list[WorkflowCheck]
    blockers: list[str]


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def read_workflow() -> str:
    return WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else ""


def build_status() -> WorkflowStatus:
    source = read_workflow()
    checks = [
        WorkflowCheck("workflow exists", WORKFLOW.exists(), str(WORKFLOW.relative_to(ROOT))),
        WorkflowCheck("workflow_dispatch enabled", "workflow_dispatch:" in source, "manual run supported"),
        WorkflowCheck("postgres service configured", "postgres:16-alpine" in source and "services:" in source, "disposable Postgres service"),
        WorkflowCheck("proof DSN configured", "AUTH_REFRESH_DB_PROOF_DSN:" in source and "127.0.0.1:55432" in source, "local service DSN"),
        WorkflowCheck("integration proof test executed", "tests/integration/test_auth_refresh_db_proof.py" in source, "DB proof test path"),
        WorkflowCheck("evidence attach executed", "make auth-refresh-db-evidence-attach" in source, "evidence attach target"),
        WorkflowCheck("evidence release check executed", "make auth-refresh-db-evidence-release-check" in source, "release evidence target"),
        WorkflowCheck("concrete run URL uses github.run_id", "actions/runs/${{ github.run_id }}" in source, "numeric run id at runtime"),
        WorkflowCheck("commit SHA uses github.sha", "AUTH_REFRESH_DB_COMMIT_SHA: ${{ github.sha }}" in source, "concrete commit SHA"),
        WorkflowCheck("artifact upload configured", "actions/upload-artifact@v4" in source, "proof artifacts uploaded"),
        WorkflowCheck("no placeholder REAL_RUN_ID", "REAL_RUN_ID" not in source, "placeholder rejected"),
        WorkflowCheck("no symbolic REAL_DSN", "$REAL_" not in source and "REAL_AUTH_REFRESH" not in source, "no REAL_* evidence placeholder"),
    ]
    blockers = [check.name for check in checks if not check.passed]
    return WorkflowStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status="ci-auth-refresh-db-proof-workflow-configured" if not blockers else "ci-auth-refresh-db-proof-workflow-not-proven",
        checks=checks,
        blockers=blockers,
    )


def write_status() -> WorkflowStatus:
    status = build_status()
    STATUS_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    lines = [
        "# CI Auth Refresh DB Proof Workflow Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]
    for check in status.checks:
        lines.append(f"| `{check.name}` | {check.passed} | {check.detail} |")
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {blocker}" for blocker in status.blockers) if status.blockers else lines.append("- None")
    lines.extend(
        [
            "",
            "## No false-closure rules",
            "",
            "- Workflow configuration does not prove the workflow has run.",
            "- Release evidence still requires a concrete GitHub Actions run URL.",
            "- This workflow does not approve beta release.",
            "",
        ]
    )
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")
    return status
