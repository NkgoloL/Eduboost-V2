#!/usr/bin/env python3
"""Generate an explicit POPIA consent-boundary matrix for V2 routes."""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ROUTER_DIR = REPO_ROOT / "app" / "api_v2_routers"

ROUTE_DECISIONS: dict[tuple[str, str], str] = {
    ("assessments.py", "list_assessments"): "authenticated_catalog_boundary",
    ("assessments.py", "submit_attempt"): "active_consent_required",
    ("consent.py", "grant_consent"): "rights_exercise_not_active_consent_blocked",
    ("consent.py", "revoke_consent"): "rights_exercise_not_active_consent_blocked",
    ("consent.py", "consent_status"): "rights_exercise_not_active_consent_blocked",
    ("diagnostics.py", "get_diagnostic_items"): "active_consent_required",
    ("diagnostics.py", "submit_diagnostic"): "active_consent_required",
    ("ether.py", "get_questions"): "authenticated_catalog_boundary",
    ("ether.py", "submit_onboarding"): "authenticated_catalog_boundary",
    ("gamification.py", "get_profile"): "active_consent_required",
    ("gamification.py", "award_xp"): "active_consent_required",
    ("gamification.py", "get_leaderboard"): "authenticated_catalog_boundary",
    ("learners.py", "create_learner"): "rights_exercise_not_active_consent_blocked",
    ("learners.py", "get_learner"): "active_consent_required",
    ("learners.py", "get_mastery"): "active_consent_required",
    ("learners.py", "request_erasure"): "rights_exercise_not_active_consent_blocked",
    ("lessons.py", "generate_lesson"): "active_consent_required",
    ("lessons.py", "generate_lesson_stream"): "active_consent_required",
    ("onboarding.py", "get_onboarding_questions"): "authenticated_catalog_boundary",
    ("onboarding.py", "submit_onboarding"): "active_consent_required",
    ("parents.py", "get_parent_dashboard"): "active_consent_required",
    ("parents.py", "get_parent_trust_dashboard"): "active_consent_required",
    ("parents.py", "export_parent_access_bundle"): "active_consent_required",
    ("parents.py", "get_learner_progress"): "active_consent_required",
    ("parents.py", "request_erasure"): "rights_exercise_not_active_consent_blocked",
    ("popia.py", "export_learner_data"): "active_consent_required",
    ("popia.py", "request_learner_deletion"): "rights_exercise_not_active_consent_blocked",
    ("popia.py", "cancel_learner_deletion"): "rights_exercise_not_active_consent_blocked",
    ("popia.py", "request_correction"): "rights_exercise_not_active_consent_blocked",
    ("popia.py", "request_processing_restriction"): "rights_exercise_not_active_consent_blocked",
    ("popia.py", "execute_learner_deletion"): "rights_exercise_not_active_consent_blocked",
    ("popia.py", "get_deletion_status"): "rights_exercise_not_active_consent_blocked",
    ("popia.py", "export_rlhf_dataset"): "non_learner_scoped",
    ("study_plans.py", "generate_study_plan"): "active_consent_required",
}


@dataclass(frozen=True)
class BoundaryRow:
    router: str
    function: str
    route: str
    method: str
    decision: str
    marker: str


def _route_decorators(node: ast.AsyncFunctionDef | ast.FunctionDef) -> list[tuple[str, str]]:
    routes: list[tuple[str, str]] = []
    for decorator in node.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        func = decorator.func
        if not isinstance(func, ast.Attribute):
            continue
        if func.attr.lower() not in {"get", "post", "put", "patch", "delete"}:
            continue

        route = ""
        if decorator.args and isinstance(decorator.args[0], ast.Constant):
            route = str(decorator.args[0].value)
        routes.append((func.attr.upper(), route))
    return routes


def _source_for_node(source: str, node: ast.AsyncFunctionDef | ast.FunctionDef) -> str:
    lines = source.splitlines()
    return "\n".join(lines[node.lineno - 1 : node.end_lineno or node.lineno])


def _marker_for(decision: str, source: str) -> str:
    if decision == "active_consent_required":
        if "require_active_consent_for_current_user" in source:
            return "require_active_consent_for_current_user"
        if "require_active_consent" in source:
            return "require_active_consent"
        return "-"
    if decision == "rights_exercise_not_active_consent_blocked":
        return "rights_exercise"
    if decision == "authenticated_catalog_boundary":
        return "get_current_user"
    return "-"


def collect_rows() -> list[BoundaryRow]:
    rows: list[BoundaryRow] = []
    if not ROUTER_DIR.exists():
        return rows

    for path in sorted(ROUTER_DIR.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                continue

            routes = _route_decorators(node)
            if not routes:
                continue

            decision = ROUTE_DECISIONS.get((path.name, node.name), "non_learner_scoped")
            marker = _marker_for(decision, _source_for_node(source, node))
            for method, route in routes:
                rows.append(
                    BoundaryRow(
                        router=path.name,
                        function=node.name,
                        route=route,
                        method=method,
                        decision=decision,
                        marker=marker,
                    )
                )

    return rows


def render(rows: list[BoundaryRow]) -> str:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.decision] = counts.get(row.decision, 0) + 1

    lines = [
        "# POPIA Consent Boundary Matrix",
        "",
        "Generated by `scripts/generate_popia_consent_boundary_matrix.py`.",
        "",
        "## Summary",
        "",
    ]
    for decision in sorted(counts):
        lines.append(f"- `{decision}`: {counts[decision]}")

    lines.extend(
        [
            "",
            "## Matrix",
            "",
            "| Router | Method | Route | Function | Decision | Marker |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )

    for row in rows:
        lines.append(
            f"| `{row.router}` | `{row.method}` | `{row.route}` | `{row.function}` | `{row.decision}` | `{row.marker}` |"
        )

    return "\n".join(lines) + "\n"


def main() -> int:
    rows = collect_rows()
    output = REPO_ROOT / "docs" / "security" / "popia_consent_boundary_matrix.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(rows), encoding="utf-8")
    print(f"Wrote {output.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
