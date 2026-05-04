from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.api_v2 import app
from app.core.security import get_current_user, require_admin, require_parent_or_admin


def _override_user():
    return {"sub": "guardian-1", "role": "admin", "jti": "test-jti"}


def _client() -> TestClient:
    app.dependency_overrides[get_current_user] = _override_user
    app.dependency_overrides[require_parent_or_admin] = _override_user
    app.dependency_overrides[require_admin] = _override_user
    return TestClient(app)


def teardown_module():
    app.dependency_overrides.clear()


def test_lesson_generation_job_flow():
    client = _client()
    with patch("app.api_v2_routers.lessons.ConsentService.require_active_consent", new=AsyncMock()), \
         patch("app.api_v2_routers.lessons.LearnerRepository.get_by_id", new=AsyncMock(return_value=type("Learner", (), {
             "id": "learner-1", "guardian_id": "guardian-1", "pseudonym_id": "pseudo-1", "grade": 4, "archetype": "Keter"
         })())), \
         patch("app.api_v2_routers.lessons.GuardianRepository.get_by_id", new=AsyncMock(return_value=type("Guardian", (), {
             "subscription_tier": "free"
         })())), \
         patch("app.api_v2_routers.lessons._executive.generate_lesson", new=AsyncMock(return_value=(type("Payload", (), {
             "title": "Fractions", "introduction": "Intro", "main_content": "Body", "worked_example": "Example",
             "practice_question": "Q", "answer": "A", "cultural_hook": "Hook"
         })(), False))), \
         patch("app.api_v2_routers.lessons.LessonRepository.create", new=AsyncMock(return_value=type("LessonRow", (), {
             "id": "lesson-1", "grade": 4, "subject": "Mathematics", "topic": "Fractions", "language": "en",
             "content": "content", "archetype": "Keter", "served_from_cache": False, "created_at": "2026-05-04T00:00:00+00:00"
         })())), \
         patch("app.api_v2_routers.lessons.FourthEstateService.lesson_generated", new=AsyncMock()):
        response = client.post("/v2/lessons/generate", json={"learner_id": "learner-1", "subject": "Mathematics", "topic": "Fractions"})
    assert response.status_code == 202
    job = client.get(f"/v2/jobs/{response.json()['job_id']}")
    assert job.status_code == 200
    assert job.json()["status"] == "completed"
    assert job.json()["result"]["id"] == "lesson-1"


def test_study_plan_generation_job_flow():
    client = _client()
    with patch("app.api_v2_routers.study_plans.StudyPlanServiceV2.generate_plan", new=AsyncMock(return_value={"plan_id": "plan-1", "learner_id": "learner-1"})), \
         patch("app.api_v2_routers.study_plans.AuditService.log_event", new=AsyncMock()):
        response = client.post("/v2/study-plans/generate/learner-1", json={"gap_ratio": 0.4})
    assert response.status_code == 202
    job = client.get(f"/v2/jobs/{response.json()['job_id']}")
    assert job.status_code == 200
    assert job.json()["status"] == "completed"
    assert job.json()["result"]["plan_id"] == "plan-1"


def test_popia_purge_job_flow():
    client = _client()
    with patch("app.api_v2_routers.popia.AsyncSessionLocal") as session_factory, \
         patch("app.api_v2_routers.popia.LearnerRepository.purge_personal_data", new=AsyncMock()), \
         patch("app.api_v2_routers.popia.FourthEstateService.record", new=AsyncMock()):
        learner = type("Learner", (), {"guardian_id": "guardian-1", "pseudonym_id": "pseudo-1"})()
        db = AsyncMock()
        db.get = AsyncMock(return_value=learner)
        db.commit = AsyncMock()
        session_factory.return_value.__aenter__.return_value = db
        response = client.post("/v2/popia/deletion-execute/learner-1")
    assert response.status_code == 202
    job = client.get(f"/v2/jobs/{response.json()['job_id']}")
    assert job.status_code == 200
    assert job.json()["status"] == "completed"
    assert job.json()["result"]["purged"] is True


def test_rlhf_export_job_flow():
    client = _client()
    response = client.post("/v2/popia/rlhf-export/openai", json={"records": [{"prompt": "Hi", "chosen": "Hello"}]})
    assert response.status_code == 202
    job = client.get(f"/v2/jobs/{response.json()['job_id']}")
    assert job.status_code == 200
    assert job.json()["status"] == "completed"
    assert job.json()["result"]["format"] == "openai"


def test_consent_renewal_job_flow():
    client = _client()
    with patch("app.api_v2_routers.consent_renewal.AsyncSessionLocal") as session_factory, \
         patch("app.api_v2_routers.consent_renewal.ConsentRenewalService.run", new=AsyncMock(return_value={"checked": 1, "reminded": 1, "failed": 0, "skipped_already_expired": 0})), \
         patch("app.api_v2_routers.consent_renewal.SendGridEmailGateway"):
        db = AsyncMock()
        session_factory.return_value.__aenter__.return_value = db
        response = client.post("/v2/admin/consent/trigger-renewal-reminders")
    assert response.status_code == 202
    job = client.get(f"/v2/jobs/{response.json()['job_id']}")
    assert job.status_code == 200
    assert job.json()["status"] == "completed"
    assert job.json()["result"]["reminded"] == 1
