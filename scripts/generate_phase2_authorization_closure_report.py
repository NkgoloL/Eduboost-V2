#!/usr/bin/env python3
"""Generate the Phase 2 learner authorization closure report."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT_BOOTSTRAP = Path(__file__).resolve().parents[1]
if str(REPO_ROOT_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT_BOOTSTRAP))


from scripts.generate_learner_authz_matrix import collect_rows

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "security" / "PHASE2_AUTHORIZATION_CLOSURE.md"

SCRIPT_NAME = "generate_phase2_authorization_closure_report"


KEY_EVIDENCE = [
    "docs/security/object_authorization.md",
    "docs/security/authorization_dependencies.md",
    "docs/security/learner_authz_matrix.md",
    "docs/security/learner_authz_coverage_check.md",
    "docs/security/learner_authz_ci.md",
    "docs/security/phase2_authorization_evidence_check.md",
]

OPERATIONAL_BOUNDARY_EVIDENCE = [
    "docs/security/dev_session_environment_gate.md",
    "docs/security/consent_renewal_admin_auth_boundary.md",
    "docs/security/ether_onboarding_questions_auth_boundary.md",
]


def _status_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in collect_rows():
        counts[row.status] = counts.get(row.status, 0) + 1
    return counts


def render() -> str:
    rows = collect_rows()
    counts = _status_counts()
    missing = [row for row in rows if row.status == "missing"]

    lines = [
        "# Phase 2 Authorization Closure Report",
        "",
        "## Scope",
        "",
        "Phase 2 covers learner-object authorization for learner-owned data routes,",
        "plus explicit authentication-boundary documentation for catalog or operational",
        "routes that do not carry a learner object.",
        "",
        "## Route Matrix Summary",
        "",
        f"- Routes inspected: {len(rows)}",
        f"- Covered learner-scoped routes: {counts.get('covered', 0)}",
        f"- Non-learner-scoped routes: {counts.get('not_learner_scoped', 0)}",
        f"- Missing learner authorization markers: {len(missing)}",
        "",
        "## Key Evidence",
        "",
    ]

    for rel_path in KEY_EVIDENCE:
        status = "present" if (REPO_ROOT / rel_path).exists() else "missing"
        lines.append(f"- `{rel_path}` — {status}")

    lines.extend(
        [
            "",
            "## Verification Commands",
            "",
            "```bash",
            "make runtime-check",
            "make openapi-check",
            "make route-inventory-check",
            "make pr002r-check",
            "make phase2-authz-check",
            "make learner-authz-check",
            "pytest -c pytest.ini tests/unit/test_phase2_authorization_evidence.py tests/unit/test_check_learner_authz_coverage.py tests/unit/test_phase2_router_import_smoke.py -q --no-cov",
            "```",
            "",
            "## Operational Auth Boundary Hardening",
            "",
            "Operational routes that do not carry a learner object are documented",
            "separately from learner-object authorization. These files define the",
            "non-production, admin-only, or authenticated-user boundary for each",
            "exception class:",
            "",
        ]
    )

    for rel_path in OPERATIONAL_BOUNDARY_EVIDENCE:
        status = "present" if (REPO_ROOT / rel_path).exists() else "missing"
        lines.append(f"- `{rel_path}` — {status}")

    lines.extend(
        [
            "",
            "Operational boundary hardening stamp: operational exceptions are explicit",
            "and remain covered by Phase 2 evidence checks.",
            "",
            "## Closure Status",
            "",
        ]
    )

    if missing:
        lines.append("Status: **not closed** — missing learner authorization markers remain.")
        lines.append("")
        for row in missing:
            lines.append(f"- `{row.router}` `{row.method} {row.path}` via `{row.function}`")
    else:
        lines.append("Status: **closure-ready** — no unallowlisted learner-scoped route is missing an authorization marker.")

    lines.extend(
        [
            "",
            "## Closure Stamp",
            "",
            "Phase 2 closure evidence is anchored by `make phase2-authz-closure`,",
            "`make learner-authz-check`, and `make phase2-authz-check`.",
        ]
    )

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(render(), encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
