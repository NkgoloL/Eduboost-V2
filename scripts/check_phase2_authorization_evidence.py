#!/usr/bin/env python3
"""Check Phase 2 authorization evidence and pilot route coverage."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/security/ether_onboarding_questions_auth_boundary.md",
    "docs/security/consent_renewal_admin_auth_boundary.md",
    "docs/security/dev_session_environment_gate.md",
    "tests/unit/test_ether_onboarding_questions_auth_boundary.py",
    "tests/unit/test_consent_renewal_admin_auth_boundary.py",
    "tests/unit/test_dev_session_environment_gate.py",
    "tests/unit/test_phase2_authorization_closure_stamp.py",
    "tests/unit/test_phase2_authorization_closure_script.py",
    "docs/security/phase2_authorization_closure_check.md",
    "scripts/check_phase2_authorization_closure.py",
    "tests/unit/test_generate_phase2_authorization_closure_report.py",
    "tests/unit/test_learner_authz_ci_contract.py",
    "scripts/generate_phase2_authorization_closure_report.py",
    "docs/security/phase2_authorization_closure_report.md",
    "docs/security/PHASE2_AUTHORIZATION_CLOSURE.md",
    "docs/security/learner_authz_ci.md",
    ".github/workflows/learner-authz-coverage.yml",
    "tests/unit/test_check_learner_authz_coverage.py",
    "tests/unit/test_generate_learner_authz_matrix.py",
    "docs/security/learner_authz_coverage_check.md",
    "docs/security/learner_authz_matrix.md",
    "scripts/check_learner_authz_coverage.py",
    "scripts/generate_learner_authz_matrix.py",
    "tests/unit/test_phase2_router_import_smoke.py",
    "tests/unit/test_assessment_attempt_model_contract.py",
    "docs/security/phase2_router_import_smoke.md",
    "docs/security/assessment_attempt_model_contract.md",
    "tests/unit/test_onboarding_questions_auth_boundary.py",
    "tests/unit/test_assessment_list_auth_boundary.py",
    "docs/security/onboarding_questions_auth_boundary.md",
    "docs/security/assessment_list_auth_boundary.md",
    "tests/unit/test_onboarding_authorization_wiring.py",
    "tests/unit/test_assessment_attempt_authorization_wiring.py",
    "docs/security/onboarding_authorization_wiring.md",
    "docs/security/assessment_attempt_authorization_wiring.md",
    "tests/integration/test_lesson_stream_authorization.py",
    "tests/unit/test_lesson_stream_authorization_wiring.py",
    "tests/integration/test_gamification_award_xp_authorization.py",
    "tests/unit/test_gamification_award_xp_authorization_wiring.py",
    "docs/security/lesson_stream_authorization_wiring.md",
    "docs/security/gamification_award_xp_authorization_wiring.md",
    "tests/integration/test_gamification_profile_authorization.py",
    "tests/unit/test_gamification_profile_authorization_wiring.py",
    "tests/integration/test_consent_revoke_authorization.py",
    "tests/unit/test_consent_revoke_authorization_wiring.py",
    "tests/integration/test_consent_grant_authorization.py",
    "tests/unit/test_consent_grant_authorization_wiring.py",
    "docs/security/gamification_profile_authorization_wiring.md",
    "docs/security/consent_revoke_authorization_wiring.md",
    "docs/security/consent_grant_authorization_wiring.md",
    "tests/unit/test_parent_dashboard_authorization_wiring.py",
    "tests/unit/test_parent_trust_dashboard_authorization_wiring.py",
    "tests/integration/test_consent_status_authorization.py",
    "tests/unit/test_consent_status_authorization_wiring.py",
    "docs/security/parent_dashboard_authorization_wiring.md",
    "docs/security/parent_trust_dashboard_authorization_wiring.md",
    "docs/security/consent_status_authorization_wiring.md",
    "tests/integration/test_parent_export_authorization.py",
    "tests/unit/test_parent_export_authorization_wiring.py",    "tests/integration/test_parent_erasure_authorization.py",
    "tests/unit/test_parent_erasure_authorization_wiring.py",
    "docs/security/parent_export_authorization_wiring.md",    "docs/security/parent_erasure_authorization_wiring.md",    "tests/unit/test_popia_restriction_request_authorization_wiring.py",
    "tests/unit/test_popia_correction_request_authorization_wiring.py",    "docs/security/popia_restriction_request_authorization_wiring.md",
    "docs/security/popia_correction_request_authorization_wiring.md",
    "tests/unit/test_popia_deletion_cancel_authorization_wiring.py",
    "tests/unit/test_popia_deletion_request_authorization_wiring.py",
    "tests/integration/test_parent_progress_authorization.py",
    "tests/unit/test_parent_progress_authorization_wiring.py",
    "tests/unit/test_popia_data_export_authorization_wiring.py",
    "tests/integration/test_diagnostic_submit_authorization.py",
    "tests/unit/test_diagnostic_submit_authorization_wiring.py",
    "tests/integration/test_popia_data_subject_rights.py",
    "docs/security/popia_deletion_cancel_authorization_wiring.md",
    "docs/security/popia_deletion_request_authorization_wiring.md",
    "docs/security/parent_progress_authorization_wiring.md",
    "docs/security/popia_data_export_authorization_wiring.md",
    "docs/security/diagnostic_submit_authorization_wiring.md",
    "app/security/object_authorization.py",
    "app/security/dependencies.py",
    "docs/security/object_authorization.md",
    "docs/security/authorization_dependencies.md",
    "docs/security/learner_route_authorization_inspection.md",
    "docs/security/learner_route_authorization_wiring.md",
    "docs/security/learner_read_authorization_http_tests.md",
    "docs/security/learner_mastery_authorization_wiring.md",
    "docs/security/study_plan_authorization_wiring.md",
    "docs/security/lesson_generation_authorization_wiring.md",
    "docs/security/diagnostic_items_authorization_wiring.md",
    "tests/unit/test_object_authorization.py",
    "tests/unit/test_security_dependencies.py",
    "tests/unit/test_learner_route_authorization_wiring.py",
    "tests/integration/test_learner_read_authorization.py",
    "tests/unit/test_learner_mastery_authorization_wiring.py",
    "tests/integration/test_learner_mastery_authorization.py",
    "tests/unit/test_study_plan_authorization_wiring.py",
    "tests/integration/test_study_plan_authorization.py",
    "tests/unit/test_lesson_generation_authorization_wiring.py",
    "tests/integration/test_lesson_generation_authorization.py",
    "tests/unit/test_diagnostic_items_authorization_wiring.py",
    "tests/integration/test_diagnostic_items_authorization.py",
)

CONTENT_REQUIREMENTS = {
    "app/api_v2_routers/onboarding.py": (
        "async def get_onboarding_questions(current_user: AuthContext = Depends(require_auth_context))",
    ),
    "scripts/generate_learner_authz_matrix.py": (
        "require_admin",
        "get_current_user",
    ),
    "docs/security/ether_onboarding_questions_auth_boundary.md": (
        "GET /api/v2/ether/onboarding/questions",
        "Depends(get_current_user)",
    ),
    "docs/security/consent_renewal_admin_auth_boundary.md": (
        "POST /api/v2/admin/consent/trigger-renewal-reminders",
        "Depends(require_admin)",
    ),
    "docs/security/dev_session_environment_gate.md": (
        "POST /api/v2/auth/dev-session",
        "settings.is_production()",
        "HTTP_404_NOT_FOUND",
    ),
    "docs/security/phase2_authorization_closure_check.md": (
        "make phase2-authz-closure",
        "make learner-authz-check",
    ),
    "scripts/check_phase2_authorization_closure.py": (
        "make",
        "phase2-authz-check",
        "learner-authz-check",
    ),
    "scripts/generate_phase2_authorization_closure_report.py": (
        "generate_phase2_authorization_closure_report",
        "collect_rows",
    ),
    "docs/security/PHASE2_AUTHORIZATION_CLOSURE.md": (
        "Phase 2 Authorization Closure Report",
        "Closure Status",
    ),
    ".github/workflows/learner-authz-coverage.yml": (
        "Learner Authorization Coverage",
        "make learner-authz-check",
    ),
    "docs/security/learner_authz_ci.md": (
        "make learner-authz-check",
        "master",
        "release/**",
    ),
    "scripts/check_learner_authz_coverage.py": (
        "ALLOWLIST",
        "collect_rows",
    ),
    "docs/security/learner_authz_coverage_check.md": (
        "make learner-authz-check",
        "authorization",
    ),
    "docs/security/learner_authz_matrix.md": (
        "Learner Authorization Coverage Matrix",
        "Missing learner authorization markers",
    ),
    "app/domain/api_v2_models.py": (
        "class AssessmentAttemptRequest",
        "class AssessmentAttemptResponseItem",
    ),
    "docs/security/phase2_router_import_smoke.md": (
        "Phase 2 Router Import Smoke",
        "assessments",
        "study_plans",
    ),
    "docs/security/assessment_attempt_model_contract.md": (
        "AssessmentAttemptRequest",
        "app/domain/api_v2_models.py",
    ),
    "docs/security/onboarding_questions_auth_boundary.md": (
        "GET /api/v2/onboarding/questions",
        "authentication",
    ),
    "docs/security/assessment_list_auth_boundary.md": (
        "GET /api/v2/assessments",
        "authenticated user",
    ),
    "docs/security/onboarding_authorization_wiring.md": (
        "POST /api/v2/onboarding/submit",
        "POST /api/v2/onboarding/archetype",
        "require_learner_write_for_current_user",
    ),
    "docs/security/assessment_attempt_authorization_wiring.md": (
        "POST /api/v2/assessments/{assessment_id}/attempt",
        "require_learner_write_for_current_user",
    ),
    "docs/security/lesson_stream_authorization_wiring.md": (
        "POST /api/v2/lessons/generate/stream",
        "require_learner_write_for_current_user",
    ),
    "docs/security/gamification_award_xp_authorization_wiring.md": (
        "POST /api/v2/gamification/award-xp",
        "require_learner_write_for_current_user",
    ),
    "docs/security/gamification_profile_authorization_wiring.md": (
        "GET /api/v2/gamification/profile/{learner_id}",
        "require_learner_read_for_current_user",
    ),
    "docs/security/consent_revoke_authorization_wiring.md": (
        "POST /api/v2/consent/revoke",
        "require_learner_write_for_current_user",
    ),
    "docs/security/consent_grant_authorization_wiring.md": (
        "POST /api/v2/consent/grant",
        "require_learner_write_for_current_user",
    ),
    "docs/security/parent_dashboard_authorization_wiring.md": (
        "GET /api/v2/parents/dashboard",
        "require_learner_read_for_current_user",
    ),
    "docs/security/parent_trust_dashboard_authorization_wiring.md": (
        "GET /api/v2/parents/{guardian_id}/dashboard",
        "require_learner_read_for_current_user",
    ),
    "docs/security/consent_status_authorization_wiring.md": (
        "GET /api/v2/consent/status/{learner_id}",
        "require_learner_read_for_current_user",
    ),
    "docs/security/parent_export_authorization_wiring.md": (
        "GET /api/v2/parents/{guardian_id}/export",
        "require_learner_read_for_current_user",
    ),    "docs/security/parent_erasure_authorization_wiring.md": (
        "DELETE /api/v2/parents/learners/{learner_id}",
        "require_learner_write_for_current_user",
    ),    "docs/security/popia_restriction_request_authorization_wiring.md": (
        "POST /api/v2/popia/restriction-request/{learner_id}",
        "require_learner_write_for_current_user",
    ),
    "docs/security/popia_correction_request_authorization_wiring.md": (
        "POST /api/v2/popia/correction-request/{learner_id}",
        "require_learner_write_for_current_user",
    ),
    "docs/security/popia_deletion_cancel_authorization_wiring.md": (
        "POST /api/v2/popia/deletion-cancel/{learner_id}",
        "require_learner_write_for_current_user",
    ),
    "docs/security/popia_deletion_request_authorization_wiring.md": (
        "POST /api/v2/popia/deletion-request/{learner_id}",
        "require_learner_write_for_current_user",
    ),
    "docs/security/parent_progress_authorization_wiring.md": (
        "GET /api/v2/parents/learners/{learner_id}/progress",
        "require_learner_read_for_current_user",
    ),
    "docs/security/popia_data_export_authorization_wiring.md": (
        "GET /api/v2/popia/data-export/{learner_id}",
        "require_learner_read_for_current_user",
    ),
    "docs/security/diagnostic_submit_authorization_wiring.md": (
        "POST /api/v2/diagnostics/submit",
        "require_learner_write_for_current_user",
    ),
    "app/api_v2_routers/parents.py": (
        "require_learner_read_for_current_user(current_user, learner)",
    ),
    "app/api_v2_routers/popia.py": (
        "dsr_svc: POPIADataRightsService",
        "await dsr_svc.build_learner_export(",
        "await dsr_svc.request_erasure(",
    ),
    "app/services/popia_service.py": (
        "require_learner_read_for_current_user(current_user, learner)",
        "require_learner_write_for_current_user(current_user, learner_id)",
    ),
    "app/api_v2_routers/learners.py": (
        "require_learner_read_for_current_user(current_user, learner)",
    ),
    "app/api_v2_routers/study_plans.py": (
        "require_learner_write_for_current_user(current_user, learner_id)",
    ),
    "app/api_v2_routers/lessons.py": (
        "require_learner_write_for_current_user(auth, str(body.learner_id))",
    ),
    "app/api_v2_routers/diagnostics.py": (
        "require_learner_read_for_current_user(current_user, learner)",
    ),
    "docs/security/study_plan_authorization_wiring.md": (
        "POST /api/v2/study-plans/{learner_id}",
        "require_learner_write_for_current_user",
    ),
    "docs/security/lesson_generation_authorization_wiring.md": (
        "POST /api/v2/lessons/generate",
        "require_learner_write_for_current_user",
    ),
    "docs/security/diagnostic_items_authorization_wiring.md": (
        "GET /api/v2/diagnostics/items/{learner_id}",
        "require_learner_read_for_current_user",
    ),
}


@dataclass(frozen=True)
class CheckResult:
    category: str
    target: str
    ok: bool
    detail: str


def check_files() -> list[CheckResult]:
    results: list[CheckResult] = []
    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            CheckResult(
                category="file",
                target=rel_path,
                ok=path.exists(),
                detail="present" if path.exists() else "missing",
            )
        )
    return results


def check_content() -> list[CheckResult]:
    results: list[CheckResult] = []
    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        if not path.exists():
            results.append(CheckResult("content", rel_path, False, "file missing"))
            continue

        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            results.append(
                CheckResult(
                    category="content",
                    target=rel_path,
                    ok=snippet in text,
                    detail=f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )
    return results


def check_all() -> list[CheckResult]:
    return [*check_files(), *check_content()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Phase 2 authorization evidence.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = check_all()

    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2, sort_keys=True))
    else:
        print("Phase 2 authorization evidence check")
        for result in results:
            status = "PASS" if result.ok else "FAIL"
            print(f"- {status} [{result.category}] {result.target}: {result.detail}")

    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
