#!/usr/bin/env python3
"""Validate production-readiness item 19: roadmap after production-readiness baseline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.modules.roadmap.production_readiness_contracts import default_post_baseline_roadmap_readiness_report


REQUIRED_FILES = (
    "app/modules/roadmap/__init__.py",
    "app/modules/roadmap/production_readiness_contracts.py",
    "docs/adr/ADR-019-roadmap-after-production-readiness-baseline.md",
    "docs/roadmap/post_baseline_roadmap_architecture_contract.md",
    "docs/roadmap/production_readiness_baseline_boundary_contract.md",
    "docs/roadmap/post_baseline_roadmap_register.md",
    "docs/roadmap/deferred_scope_register.md",
    "docs/roadmap/roadmap_dependency_register.md",
    "docs/roadmap/roadmap_graduation_criteria.md",
    "docs/roadmap/roadmap_review_cadence_contract.md",
    "docs/roadmap/post_baseline_risk_register.md",
    "docs/roadmap/ga_graduation_boundary_contract.md",
    "docs/backlog/production_readiness/19_roadmap_after_production-readiness_baseline.md",
    "tests/unit/test_roadmap_after_production_readiness_baseline.py",
)

CONTENT_REQUIREMENTS = {
    "app/modules/roadmap/production_readiness_contracts.py": (
        "class RoadmapHorizon",
        "class RoadmapCategory",
        "class RoadmapStatus",
        "class BaselineBoundary",
        "class DependencyType",
        "class PriorityLevel",
        "RoadmapGovernanceDecision",
        "BaselineBoundaryItem",
        "RoadmapItem",
        "DeferredScopeItem",
        "RoadmapDependency",
        "GraduationCriterion",
        "RoadmapReviewCadence",
        "PostBaselineRisk",
        "compute_roadmap_checksum",
        "summarize_roadmap_horizons",
        "validate_roadmap_bundle",
        "default_post_baseline_roadmap_readiness_report",
    ),
    "docs/adr/ADR-019-roadmap-after-production-readiness-baseline.md": (
        "Roadmap After Production-Readiness Baseline",
        "roadmap owner is required",
        "deferred scope register is required",
        "dependency mapping is required",
        "graduation criteria are required",
        "external/manual dependencies must be explicit",
    ),
    "docs/roadmap/post_baseline_roadmap_architecture_contract.md": (
        "Post-Baseline Roadmap Architecture Contract",
        "baseline boundary register",
        "post-baseline roadmap register",
        "deferred scope register",
        "roadmap dependency register",
        "post-baseline risk register",
        "explicit external/manual dependencies",
    ),
    "docs/roadmap/production_readiness_baseline_boundary_contract.md": (
        "Production Readiness Baseline Boundary Contract",
        "included",
        "deferred",
        "excluded",
        "external manual",
        "external/manual boundary requires manual dependency",
    ),
    "docs/roadmap/post_baseline_roadmap_register.md": (
        "Post-Baseline Roadmap Register",
        "Live billing provider integration",
        "Production telemetry dashboard implementation",
        "Advanced mastery-model research",
        "Public beta expansion",
        "roadmap ID must follow RM-### format",
    ),
    "docs/roadmap/deferred_scope_register.md": (
        "Deferred Scope Register",
        "Live payment processing",
        "General availability launch",
        "unblock condition is required",
        "deferred scope review date must not be stale",
    ),
    "docs/roadmap/roadmap_dependency_register.md": (
        "Roadmap Dependency Register",
        "dependency ID must follow DEP-### format",
        "source roadmap ID must follow RM-### format",
        "external dependencies require mitigation",
    ),
    "docs/roadmap/roadmap_graduation_criteria.md": (
        "Roadmap Graduation Criteria",
        "billing_webhook_success_rate",
        "dashboard_alert_route_coverage",
        "beta_exit_criteria_passed",
    ),
    "docs/roadmap/roadmap_review_cadence_contract.md": (
        "Roadmap Review Cadence Contract",
        "beta feedback",
        "known issues",
        "security findings",
        "blocks scope expansion",
    ),
    "docs/roadmap/post_baseline_risk_register.md": (
        "Post-Baseline Risk Register",
        "risk ID must follow RISK-### format",
        "critical post-baseline risk must block GA",
        "risk evidence path must live under docs/roadmap/",
    ),
    "docs/roadmap/ga_graduation_boundary_contract.md": (
        "GA Graduation Boundary Contract",
        "beta exit criteria must be reviewed",
        "production launch approval must be separate",
        "live billing must remain disabled until approved",
        "critical post-baseline risks must block GA",
    ),
    "docs/backlog/production_readiness/19_roadmap_after_production-readiness_baseline.md": (
        "19.6 Repository-side implementation evidence",
        "docs/roadmap/post_baseline_roadmap_architecture_contract.md",
        "scripts/check_roadmap_after_production_readiness_baseline.py",
        "make roadmap-after-production-readiness-baseline-check",
    ),
    "Makefile": (
        "roadmap-after-production-readiness-baseline-check:",
        "scripts/check_roadmap_after_production_readiness_baseline.py",
    ),
}


@dataclass(frozen=True)
class RoadmapReadinessResult:
    target: str
    ok: bool
    detail: str


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[RoadmapReadinessResult]:
    results: list[RoadmapReadinessResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(RoadmapReadinessResult(rel_path, path.exists(), "file present" if path.exists() else "file missing"))

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = _read(rel_path)
        for snippet in snippets:
            results.append(
                RoadmapReadinessResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    try:
        report = default_post_baseline_roadmap_readiness_report()
        results.extend(
            [
                RoadmapReadinessResult("roadmap_contracts", report["decision_issues"] == [], "roadmap decision validates"),
                RoadmapReadinessResult("roadmap_contracts", report["baseline_boundary_issues"] == [], "baseline boundaries validate"),
                RoadmapReadinessResult("roadmap_contracts", report["roadmap_item_issues"] == [], "roadmap items validate"),
                RoadmapReadinessResult("roadmap_contracts", report["deferred_scope_issues"] == [], "deferred scope validates"),
                RoadmapReadinessResult("roadmap_contracts", report["dependency_issues"] == [], "dependencies validate"),
                RoadmapReadinessResult("roadmap_contracts", report["graduation_criteria_issues"] == [], "graduation criteria validate"),
                RoadmapReadinessResult("roadmap_contracts", report["review_cadence_issues"] == [], "review cadence validates"),
                RoadmapReadinessResult("roadmap_contracts", report["post_baseline_risk_issues"] == [], "post-baseline risks validate"),
                RoadmapReadinessResult("roadmap_contracts", report["roadmap_bundle_issues"] == [], "roadmap bundle validates"),
                RoadmapReadinessResult("roadmap_contracts", report["horizon_summary"].get("next") == 2, "horizon summary sample passes"),
                RoadmapReadinessResult("roadmap_contracts", len(str(report["checksum_sample"])) == 64, "roadmap checksum sample passes"),
            ]
        )
    except Exception as exc:  # pragma: no cover
        results.append(RoadmapReadinessResult("roadmap_contracts", False, f"contract check failed: {exc}"))

    return results


def main() -> int:
    results = run_checks()
    print("Roadmap after production readiness baseline check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
