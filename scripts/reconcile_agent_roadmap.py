#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/roadmap/agent_roadmap_reconciliation.json"
OUT_MD = ROOT / "docs/roadmap/agent_roadmap_reconciliation.md"

@dataclass(frozen=True)
class Task:
    id: str
    priority: str
    area: str
    title: str
    status: str
    evidence: list[str]
    next_action: str

TASKS = [
    Task("T-01", "P0", "CI/CD", "Trigger GitHub Actions CI on fork", "PENDING_HUMAN", ["docs/release/ci_evidence.md"], "Enable Actions and archive first green run URL."),
    Task("T-02", "P0", "CI/CD", "Fix README CI badge", "PENDING_AGENT", ["README.md"], "Patch badge owner/repo to this fork."),
    Task("T-03", "P0", "CI/CD", "Enable branch protection", "PENDING_HUMAN", ["docs/release/branch_protection_evidence.md"], "Configure branch protection and archive evidence."),
    Task("T-04", "P0", "Testing", "Warning integrity check", "PENDING_AGENT", ["docs/release/warning_integrity_evidence.md"], "Run warning-as-error target and fix failures."),
    Task("T-05", "P1", "Content", "Educator item review and beta content gate", "PENDING_AGENT_AND_HUMAN", ["docs/beta/item_review_process.md", "docs/beta/item_review_log.md"], "Create review process and enforce threshold check."),
    Task("T-06", "P1", "Docker", "Remove --reload from base Compose", "PENDING_AGENT", ["docker-compose.yml"], "Move dev reload to override example."),
    Task("T-07", "P1", "Docker", "Frontend production build", "PENDING_AGENT", ["docker/Dockerfile.frontend", "app/frontend/next.config.*"], "Verify or implement production runner target."),
    Task("T-08", "P1", "Docker", "Compose resource limits", "PENDING_AGENT", ["docker-compose.yml", "docker-compose.prod.yml"], "Patch/check resource limits."),
    Task("T-09", "P1", "Docker/Security", "Require Grafana admin secret", "PENDING_AGENT", ["docker-compose.yml", ".env.example"], "Replace admin fallback with required variable."),
    Task("T-10", "P1", "Docker", "Add nginx production config", "PENDING_AGENT", ["nginx/nginx.conf"], "Create missing reverse-proxy config."),
    Task("T-11", "P1", "Security", "Login rate limiting/account lockout", "PENDING_AGENT", ["docs/security/auth_hardening_status.md"], "Probe current implementation and patch if absent."),
    Task("T-12R", "P2", "Architecture", "Service boundary consolidation without deleting active facades", "PENDING_AGENT", ["docs/roadmap/service_boundary_consolidation.md"], "Inventory app/services vs app/modules; migrate only proven duplicates."),
    Task("T-13", "P1", "Governance", "PR template and CODEOWNERS", "PENDING_AGENT", [".github/PULL_REQUEST_TEMPLATE.md", ".github/CODEOWNERS"], "Create governance files."),
    Task("T-14", "P1", "POPIA", "Run POPIA sweep and archive evidence", "PENDING_INFRA", ["docs/release/popia_sweep_evidence.md"], "Run sweep in configured environment and commit output."),
    Task("T-15", "P2", "Dependencies", "Pin Python dependencies", "PENDING_AGENT", ["requirements/*.txt"], "Run pip-compile in clean dependency PR."),
    Task("T-16", "P2", "Security", "JWT key rotation", "PENDING_AGENT", ["docs/security/jwt_rotation_plan.md"], "Implement kid/current/previous strategy and revoke-all."),
    Task("T-17", "P2", "Testing", "Object-level authz for every router", "PARTIAL", ["tests/integration/test_learner_read_authorization.py"], "Extend coverage to every ID-parameterized route."),
    Task("T-18", "P2", "Observability", "Alertmanager live notification", "PENDING_INFRA", ["docs/release/alertmanager_evidence.md"], "Wire notification secret and fire test alert."),
    Task("T-19", "P2", "Operations", "Backup/restore drill", "PENDING_INFRA", ["docs/release/backup_restore_evidence.md"], "Execute real drill and archive output."),
    Task("T-20", "P2", "Localisation", "Multilingual educator validation", "PENDING_HUMAN", ["docs/beta/multilingual_review_process.md"], "Collect reviewer signoff."),
    Task("T-21", "P3", "Frontend", "Bundle analysis/performance budget", "PENDING_AGENT", ["app/frontend/package.json"], "Add analyser/budget after production build is stable."),
    Task("T-22", "P3", "Architecture", "ADRs for major decisions", "PARTIAL", ["docs/adr"], "Reconcile existing ADRs and add missing decisions."),
]

def exists(path: str) -> bool:
    return bool(list(ROOT.glob(path))) if "*" in path else (ROOT / path).exists()

def refine(task: Task) -> Task:
    if task.evidence and all(exists(item) for item in task.evidence):
        if task.status.startswith("PENDING_") or task.status == "PARTIAL":
            return Task(task.id, task.priority, task.area, task.title, "PARTIAL_OR_DONE_VERIFY", task.evidence, "Run task-specific checker and confirm evidence freshness.")
    return task

def main() -> int:
    tasks = [refine(task) for task in TASKS]
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps([asdict(task) for task in tasks], indent=2), encoding="utf-8")
    lines = [
        "# Agent Roadmap Reconciliation",
        "",
        "**North Star:** Convert post-530 repository completion into beta readiness by closing CI, Docker, content-review, POPIA, auth-hardening, and operational evidence gaps.",
        "",
        "| ID | Priority | Area | Status | Task | Next action |",
        "|---|---|---|---|---|---|",
    ]
    for task in tasks:
        lines.append(f"| {task.id} | {task.priority} | {task.area} | {task.status} | {task.title} | {task.next_action} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
