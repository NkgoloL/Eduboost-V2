"""Generate complete CI authority matrix and workflow inventory.

Implements deliverables for:
- TSR-4.1: Inventory all workflows
- TSR-4.2: Define required-check authority
- TSR-4.11: Archive superseded workflows index
"""
from __future__ import annotations

import json
import yaml
from pathlib import Path
from typing import Any

from scripts.true_state_remediation.core import atomic_write_json, atomic_write_text, root_from, utc_now


CANONICAL_SIX = {
    "pr-core.yml": {
        "purpose": "Compile, fast product unit tests, Ruff, mypy, architecture gates, route & OpenAPI checks",
        "triggers": ["pull_request", "push:master"],
        "required": True,
        "replacement": "Consolidates all PR static/unit/compile checks",
        "retirement_decision": "Retained as canonical workflow #1",
    },
    "product-runtime.yml": {
        "purpose": "Product integration tests, disposable Postgres/pgvector/Redis runtime services, migrations, and critical learner journeys",
        "triggers": ["pull_request", "push:master"],
        "required": True,
        "replacement": "Consolidates all backend runtime and DB integration checks",
        "retirement_decision": "Retained as canonical workflow #2",
    },
    "frontend-e2e.yml": {
        "purpose": "Frozen Next.js install, type-check, lint, production build, Playwright and accessibility checks",
        "triggers": ["pull_request", "push:master"],
        "required": True,
        "replacement": "Consolidates frontend builds, audits, and E2E journeys",
        "retirement_decision": "Retained as canonical workflow #3",
    },
    "security-supply-chain.yml": {
        "purpose": "Bandit, pip-audit, pnpm audit, secret scan baseline, CycloneDX SBOM generation, container vulnerability checks",
        "triggers": ["pull_request", "push:master", "schedule:daily"],
        "required": True,
        "replacement": "Consolidates security scanners, dependency audits, and SBOMs",
        "retirement_decision": "Retained as canonical workflow #4",
    },
    "release-evidence.yml": {
        "purpose": "Exact-commit immutable release candidate evidence generation and hash verification",
        "triggers": ["workflow_dispatch"],
        "required": False,
        "replacement": "Consolidates release-candidate evidence collection",
        "retirement_decision": "Retained as canonical workflow #5",
    },
    "operations-drills.yml": {
        "purpose": "Database backup/restore dry runs, rollback tests, resilience verification, and incident drills",
        "triggers": ["workflow_dispatch", "schedule:weekly"],
        "required": False,
        "replacement": "Consolidates operational and resilience drill suites",
        "retirement_decision": "Retained as canonical workflow #6",
    },
}


def inventory_workflows(root: Path) -> dict[str, Any]:
    wf_dir = root / ".github/workflows"
    archive_dir = root / "archive/github_workflows"
    
    workflows: dict[str, Any] = {}
    for p in sorted(list(wf_dir.glob("*.yml")) + list(archive_dir.glob("*.yml"))):
        try:
            content = p.read_text()
            data = yaml.safe_load(content) or {}
            name = data.get("name", p.stem)
            jobs = list(data.get("jobs", {}).keys())
            
            is_canonical = p.name in CANONICAL_SIX
            status = "canonical" if is_canonical else "superseded_archived"
            
            canon_meta = CANONICAL_SIX.get(p.name, {})
            
            workflows[p.name] = {
                "file": p.name,
                "current_location": str(p.relative_to(root)),
                "name": name,
                "status": status,
                "purpose": canon_meta.get("purpose", f"Superseded audit/milestone workflow ({name}) consolidated into canonical graph"),
                "triggers": canon_meta.get("triggers", list(data.get("on", {}).keys()) if isinstance(data.get("on"), dict) else [str(data.get("on"))]),
                "required_for_pr": canon_meta.get("required", False),
                "replacement_target": canon_meta.get("replacement", "pr-core.yml / product-runtime.yml / security-supply-chain.yml"),
                "retirement_decision": canon_meta.get("retirement_decision", "Archived to archive/github_workflows/ to prevent uncoordinated CI triggers"),
                "job_count": len(jobs),
                "jobs": jobs,
            }
        except Exception as e:
            workflows[p.name] = {"file": p.name, "error": str(e)}

    # Map required branch protection checks
    required_checks = {
        "pr-core": {
            "workflow": "pr-core.yml",
            "jobs": ["compile-and-lint", "mypy-typecheck", "fast-unit-tests", "route-contract-audit"],
        },
        "product-runtime": {
            "workflow": "product-runtime.yml",
            "jobs": ["runtime-services-integration", "migration-dryrun"],
        },
        "frontend-e2e": {
            "workflow": "frontend-e2e.yml",
            "jobs": ["frontend-typecheck-and-lint", "frontend-build", "playwright-e2e"],
        },
        "security-supply-chain": {
            "workflow": "security-supply-chain.yml",
            "jobs": ["bandit-static-security", "pip-audit-dependencies", "pnpm-audit-dependencies", "secrets-baseline-check"],
        },
    }

    authority_matrix = {
        "schema_version": "eduboost/ci/authority-matrix/v1",
        "generated_at": utc_now(),
        "total_workflows_tracked": len(workflows),
        "canonical_workflow_count": len(CANONICAL_SIX),
        "archived_workflow_count": len(workflows) - len(CANONICAL_SIX),
        "required_branch_protection_checks": required_checks,
        "workflows": workflows,
    }

    # Save JSON authority matrix
    json_path = root / "docs/ci/ci_authority_matrix.json"
    atomic_write_json(json_path, authority_matrix)

    # Generate Markdown Workflow Inventory
    md_lines = [
        "# EduBoost V2 CI Workflow Authority & Inventory",
        "",
        f"**Generated**: {utc_now()}  ",
        f"**Total Workflows Tracked**: {len(workflows)}  ",
        f"**Canonical Active Workflows**: {len(CANONICAL_SIX)}  ",
        f"**Archived / Superseded Workflows**: {len(workflows) - len(CANONICAL_SIX)}  ",
        "",
        "## 1. Canonical Six-Workflow Target Graph",
        "",
        "| Workflow File | Purpose | PR Required | Triggers | Replacement / Consolidation Role |",
        "|---|---|---|---|---|",
    ]
    for c_file, c_meta in CANONICAL_SIX.items():
        md_lines.append(f"| `{c_file}` | {c_meta['purpose']} | **{'YES' if c_meta['required'] else 'NO'}** | `{', '.join(c_meta['triggers'])}` | {c_meta['replacement']} |")

    md_lines.extend([
        "",
        "## 2. Superseded & Archived Workflows Index",
        "",
        "The following workflows represent historical PRD milestone audits, legacy multi-branch triggers, and fragmented checkers. All have been consolidated and archived to `archive/github_workflows/` to prevent uncoordinated CI dispatch.",
        "",
        "| File | Original Name | Job Count | Consolidated Target |",
        "|---|---|---|---|",
    ])
    for w_name, w_info in sorted(workflows.items()):
        if w_name in CANONICAL_SIX:
            continue
        md_lines.append(f"| `{w_name}` | {w_info.get('name', 'N/A')} | {w_info.get('job_count', 0)} | `{w_info.get('replacement_target', 'Canonical Graph')}` |")

    atomic_write_text(root / "docs/ci/ci_workflow_inventory.md", "\n".join(md_lines) + "\n")
    return authority_matrix


if __name__ == "__main__":
    matrix = inventory_workflows(root_from(Path(".")))
    print(f"Generated CI authority matrix with {matrix['total_workflows_tracked']} workflows.")
