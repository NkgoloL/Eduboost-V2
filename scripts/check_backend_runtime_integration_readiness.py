#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from app.services.backend_runtime_integration_readiness import (
    blocked_changes,
    run_runtime_integration_dry_runs_sync,
    safe_dry_run_targets,
)


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    Path("docs/release/backend_runtime_integration_readiness.md"),
    Path("docs/release/audit_runtime_integration_target_map.md"),
    Path("docs/release/consent_runtime_integration_target_map.md"),
    Path("docs/release/deep_readiness_runtime_integration_target_map.md"),
    Path("docs/release/runtime_integration_boundary_policy.md"),
    Path("docs/pr/runtime_integration_pr_template.md"),
    Path("docs/release/runtime_integration_rollback_checklist.md"),
    Path("docs/release/runtime_integration_test_evidence_template.md"),
    Path("docs/release/backend_runtime_integration_next_pr_queue.md"),
    Path("docs/release/backend_runtime_integration_status_rollup.md"),
]


def main() -> int:
    failures: list[str] = []
    print("Backend runtime integration readiness check")

    targets = safe_dry_run_targets()
    if len(targets) >= 3:
        print(f"- PASS safe dry-run targets: {len(targets)}")
    else:
        print(f"- FAIL insufficient safe dry-run targets: {len(targets)}")
        failures.append("insufficient targets")

    for result in run_runtime_integration_dry_runs_sync():
        status = "PASS" if result.passed else "FAIL"
        print(f"- {status} [{result.target_id}] {result.message}: {result.details}")
        if not result.passed:
            failures.append(result.target_id)

    blocked = blocked_changes()
    for expected in ["route registration", "schema migration", "production DB mutation", "alembic stamp head"]:
        if expected in blocked:
            print(f"- PASS blocked change listed: {expected}")
        else:
            print(f"- FAIL blocked change missing: {expected}")
            failures.append(f"missing blocked change {expected}")

    for doc in REQUIRED_DOCS:
        path = REPO_ROOT / doc
        if path.exists():
            print(f"- PASS [doc] {doc}: present")
        else:
            print(f"- FAIL [doc] {doc}: missing")
            failures.append(f"missing {doc}")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS backend runtime integration readiness")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
