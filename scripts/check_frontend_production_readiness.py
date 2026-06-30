#!/usr/bin/env python3
"""Validate production frontend readiness evidence for backlog item 08."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "app/frontend/src/lib/productionReadiness/contracts.ts",
    "app/frontend/src/lib/env.ts",
    "app/frontend/src/lib/api/client.ts",
    "app/frontend/src/lib/api/types.ts",
    "app/frontend/src/lib/api/offlineSync.ts",
    "app/frontend/src/components/eduboost/RouteGuard.tsx",
    "app/frontend/src/components/ServiceWorkerRegistration.tsx",
    "app/frontend/src/app/(auth)/login/page.tsx",
    "app/frontend/src/app/(auth)/register/page.tsx",
    "app/frontend/src/app/(learner)/dashboard/page.tsx",
    "app/frontend/src/app/(learner)/diagnostic/page.tsx",
    "app/frontend/src/app/(learner)/lesson/page.tsx",
    "app/frontend/src/app/(parent)/parent-dashboard/page.tsx",
    "docs/frontend/production_frontend_env_security_contract.md",
    "docs/frontend/production_frontend_api_client_contract.md",
    "docs/frontend/production_auth_onboarding_ux_contract.md",
    "docs/frontend/production_protected_route_guard_contract.md",
    "docs/frontend/production_learner_parent_ux_contract.md",
    "docs/frontend/production_parent_privacy_controls_contract.md",
    "docs/frontend/production_teacher_admin_scope_contract.md",
    "docs/frontend/production_frontend_ux_accessibility_mobile_contract.md",
    "docs/frontend/production_frontend_pwa_low_data_contract.md",
    "docs/backlog/production_readiness/08_frontend_production_readiness_and_ux.md",
)

CONTENT_REQUIREMENTS = {
    "app/frontend/src/lib/productionReadiness/contracts.ts": (
        "PUBLIC_FRONTEND_ENV_CONTRACT",
        "SERVER_SECRET_ENV_DENYLIST_PATTERNS",
        "API_CLIENT_PRODUCTION_CONTRACT",
        "ROUTE_GUARD_MATRIX",
        "FRONTEND_UX_CAPABILITIES",
        "NEXT_PUBLIC_API_URL",
        "NEXT_PUBLIC_APP_ENV",
        "NEXT_PUBLIC_ENABLE_DEV_SESSION",
        "consumesCanonicalEnvelope",
        "normalizesErrorEnvelope",
        "propagatesRequestId",
        "refreshesExpiredSession",
        "detectsOfflineNetworkState",
        "handlesStaleData",
        "teacher-dashboard",
        "admin-dashboard",
        "WCAG 2.1 AA accessibility",
        "PWA service worker and manifest",
    ),
    "docs/frontend/production_frontend_env_security_contract.md": (
        "Separate browser-safe environment variables from server-only secrets.",
        "Ensure no secrets are exposed through `NEXT_PUBLIC_*`.",
        "Add frontend env validation script to CI.",
        "Add safe public API URL configuration.",
        "Add typed environment schema.",
        "Add staging frontend env validation.",
        "Add production frontend env validation.",
        "Document frontend environment variables.",
    ),
    "docs/frontend/production_frontend_api_client_contract.md": (
        "consume canonical PR-002R envelope",
        "Normalize error handling against canonical error envelope.",
        "Add auth token handling.",
        "Add refresh handling.",
        "Add request ID propagation.",
        "Add typed response parsing.",
        "Add typed error parsing.",
        "Add retry behavior for safe idempotent requests.",
        "Add network-offline detection.",
        "Add stale-data handling.",
        "Add API client tests.",
    ),
    "docs/frontend/production_auth_onboarding_ux_contract.md": (
        "Complete guardian signup screen.",
        "Complete guardian login screen.",
        "Complete logout UX.",
        "Complete session-expiry UX.",
        "Complete password reset request screen.",
        "Complete password reset completion screen.",
        "Complete email verification UX.",
        "Complete learner profile creation.",
        "Complete grade selection.",
        "Complete subject selection.",
        "Complete parental consent capture.",
        "Complete onboarding completion route.",
    ),
    "docs/frontend/production_protected_route_guard_contract.md": (
        "Add protected route guard for learner dashboard.",
        "Add protected route guard for parent dashboard.",
        "Add protected route guard for teacher dashboard.",
        "Add protected route guard for admin dashboard.",
        "Add role-based redirect rules.",
        "Add unauthorized state.",
        "Add forbidden state.",
    ),
    "docs/frontend/production_learner_parent_ux_contract.md": (
        "Complete learner dashboard.",
        "Show study plan.",
        "Show next recommended lesson.",
        "Show progress.",
        "Show streak if gamification enabled.",
        "Complete diagnostic question display.",
        "Complete diagnostic answer submission.",
        "Complete lesson explanation view.",
        "Complete parent dashboard.",
        "Show child progress.",
        "Show consent status.",
        "Add data export request UI.",
        "Add erasure request UI.",
        "Add data correction request UI.",
        "Add processing restriction request UI.",
    ),
    "docs/frontend/production_teacher_admin_scope_contract.md": (
        "Build teacher dashboard if in beta scope.",
        "Build admin console if in beta scope.",
        "Build audit dashboard.",
        "Build content review queue.",
        "Build class-level diagnostics.",
        "Build intervention groups.",
        "Build topic heatmaps.",
        "Build curriculum coverage admin view.",
    ),
    "docs/frontend/production_frontend_ux_accessibility_mobile_contract.md": (
        "Meet WCAG 2.1 AA for signup.",
        "Meet WCAG 2.1 AA for login.",
        "Meet WCAG 2.1 AA for consent.",
        "Meet WCAG 2.1 AA for diagnostic.",
        "Meet WCAG 2.1 AA for lesson.",
        "Meet WCAG 2.1 AA for dashboards.",
        "Add keyboard navigation tests.",
        "Ensure sufficient color contrast.",
        "Add accessible form validation.",
        "Add semantic headings.",
        "Add landmarks.",
        "Add screen-reader friendly diagnostic questions.",
        "Make all learner flows usable on mobile.",
        "Make all parent flows usable on mobile.",
    ),
    "docs/frontend/production_frontend_pwa_low_data_contract.md": (
        "Add or verify service worker.",
        "Add or verify manifest.",
        "Cache app shell.",
        "Add offline-friendly lesson content.",
        "Add offline messaging.",
        "Add compressed assets.",
        "Add low-data mode.",
        "Add PWA installability test.",
        "Add offline E2E test.",
        "Add offline feedback queue.",
        "Add sync-on-reconnect behavior.",
    ),
    "docs/backlog/production_readiness/08_frontend_production_readiness_and_ux.md": (
        "8.10 Repository-side implementation evidence",
        "make frontend-production-readiness-check",
        "app/frontend/src/lib/productionReadiness/contracts.ts",
        "docs/frontend/production_frontend_env_security_contract.md",
        "docs/frontend/production_frontend_api_client_contract.md",
        "docs/frontend/production_frontend_pwa_low_data_contract.md",
    ),
    "Makefile": (
        "frontend-production-readiness-check:",
        "scripts/check_frontend_production_readiness.py",
    ),
}

DOMAIN_REQUIREMENTS = (
    "docs/frontend/production_frontend_env_security_contract.md",
    "docs/frontend/production_frontend_api_client_contract.md",
    "docs/frontend/production_auth_onboarding_ux_contract.md",
    "docs/frontend/production_protected_route_guard_contract.md",
    "docs/frontend/production_learner_parent_ux_contract.md",
    "docs/frontend/production_frontend_ux_accessibility_mobile_contract.md",
    "docs/frontend/production_frontend_pwa_low_data_contract.md",
    "scripts/check_frontend_production_readiness.py",
)


@dataclass(frozen=True)
class FrontendProductionReadinessResult:
    target: str
    ok: bool
    detail: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[FrontendProductionReadinessResult]:
    results: list[FrontendProductionReadinessResult] = []

    for relative_path in REQUIRED_FILES:
        path = REPO_ROOT / relative_path
        results.append(
            FrontendProductionReadinessResult(
                relative_path,
                path.exists(),
                "file present" if path.exists() else "file missing",
            )
        )

    makefile = REPO_ROOT / "Makefile"
    if makefile.exists():
        CONTENT_REQUIREMENTS.setdefault("Makefile", ("frontend-production-readiness-check:", "scripts/check_frontend_production_readiness.py"))

    for relative_path, snippets in CONTENT_REQUIREMENTS.items():
        text = read_text(REPO_ROOT / relative_path)
        for snippet in snippets:
            results.append(
                FrontendProductionReadinessResult(
                    relative_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    domain_checker = REPO_ROOT / "scripts" / "check_domain_08_frontend_evidence.py"
    domain_text = read_text(domain_checker)
    for snippet in DOMAIN_REQUIREMENTS:
        results.append(
            FrontendProductionReadinessResult(
                "scripts/check_domain_08_frontend_evidence.py",
                snippet in domain_text,
                f"domain checker references {snippet!r}" if snippet in domain_text else f"domain checker missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Frontend production readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
