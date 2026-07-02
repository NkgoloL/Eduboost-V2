from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def read(path: str) -> str:
    return (ROOT / path).read_text()

def test_seeded_dynamic_routes_exist() -> None:
    for rel in [
        "app/frontend/src/app/learners/[learnerId]/page.tsx",
        "app/frontend/src/app/learners/[learnerId]/diagnostic/page.tsx",
        "app/frontend/src/app/learners/[learnerId]/diagnostic/results/page.tsx",
        "app/frontend/src/app/learners/[learnerId]/plan/page.tsx",
        "app/frontend/src/app/learners/[learnerId]/lesson/page.tsx",
        "app/frontend/src/app/parent/learners/[learnerId]/report/page.tsx",
        "app/frontend/src/app/parent/learners/[learnerId]/consent/page.tsx",
        "app/frontend/src/app/parent/learners/[learnerId]/data/page.tsx",
    ]:
        assert (ROOT / rel).exists(), rel

def test_seeded_auth_token_forwarding_present() -> None:
    assert "guardian_token" in read("app/frontend/src/lib/api/client.ts")
    assert "authorization" in read("app/frontend/src/app/api/backend/[...path]/route.ts")

def test_seeded_specs_use_async_job_contract_and_current_consent_route() -> None:
    assert "expectAcceptedJob" in read("tests/e2e/study_plan_and_lesson.spec.ts")
    assert "/consent/status/${learnerId}" in read("tests/e2e/parent_portal.spec.ts")

def test_seeded_ui_contract_markers_present() -> None:
    assert "plan-week-card" in read("app/frontend/src/app/(learner)/plan/page.tsx")
    assert "lesson-content" in read("app/frontend/src/components/eduboost/InteractiveLesson.tsx")
