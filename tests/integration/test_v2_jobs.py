from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration


from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.api_v2 import app
from app.core.security import get_current_user, require_admin, require_parent_or_admin
from app.core.jobs import create_job, run_job


def _override_user():
    return {"sub": "00000000-0000-0000-0000-000000000002", "role": "admin", "jti": "test-jti"}


def _client() -> TestClient:
    app.dependency_overrides[get_current_user] = _override_user
    app.dependency_overrides[require_parent_or_admin] = _override_user
    app.dependency_overrides[require_admin] = _override_user
    return TestClient(app)


def teardown_module():
    app.dependency_overrides.clear()


async def _mock_enqueue(background_tasks, *, operation, handler, payload=None):
    job = await create_job(operation, payload=payload)
    await run_job(job["job_id"], handler)
    return job


def test_lesson_generation_job_flow():
    client = _client()
    with patch("app.api_v2_routers.lessons.require_active_consent_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.lessons.enqueue_job", side_effect=_mock_enqueue), \
         patch("app.api_v2_routers.lessons.LessonService.generate_lesson_for_learner") as mock_gen:
        mock_gen.return_value = (
            type("LessonResponse", (), {"model_dump": lambda self, mode="json": {"id": "lesson-1"}}) (),
            False,
            "openai"
        )
        response = client.post("/v2/lessons/generate", json={"learner_id": "00000000-0000-0000-0000-000000000001", "subject": "Mathematics", "topic": "Fractions"})
    assert response.status_code == 202
    job = client.get(f"/v2/jobs/{response.json()['data']['job_id']}")
    assert job.status_code == 200
    assert job.json()["data"]["status"] == "completed"
    assert job.json()["data"]["result"]["id"] == "lesson-1"


def test_study_plan_generation_job_flow():
    client = _client()
    with patch("app.api_v2_routers.study_plans.require_active_consent_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.study_plans.enqueue_job", side_effect=_mock_enqueue), \
         patch("app.api_v2_routers.study_plans.StudyPlanServiceV2.generate_plan", new=AsyncMock(return_value={"plan_id": "plan-1", "learner_id": "learner-1"})), \
         patch("app.api_v2_routers.study_plans.AuditService.log_event", new=AsyncMock()), \
         patch("app.api_v2_routers.study_plans.TelemetryService.track_event_async", new=AsyncMock()):
        response = client.post("/v2/study-plans/generate/00000000-0000-0000-0000-000000000001", json={"gap_ratio": 0.4})
    assert response.status_code == 202
    job = client.get(f"/v2/jobs/{response.json()['data']['job_id']}")
    assert job.status_code == 200
    assert job.json()["data"]["status"] == "completed"
    assert job.json()["data"]["result"]["plan_id"] == "plan-1"


def test_popia_purge_job_flow():
    client = _client()
    with patch("app.core.database.AsyncSessionLocal") as session_factory, \
         patch("app.api_v2_routers.popia.enqueue_job", side_effect=_mock_enqueue), \
         patch("app.api_v2_routers.popia.LearnerRepository.get_by_id") as mock_get, \
         patch("app.api_v2_routers.popia.LearnerRepository.purge_personal_data", new=AsyncMock()), \
         patch("app.api_v2_routers.popia.FourthEstateService") as mock_audit_cls:
        mock_audit_cls.return_value.record = AsyncMock()
        learner = type("Learner", (), {"id": "00000000-0000-0000-0000-000000000001", "guardian_id": "00000000-0000-0000-0000-000000000002", "pseudonym_id": "pseudo-1"})()
        mock_get.return_value = learner
        db = AsyncMock()
        db.get = AsyncMock(return_value=learner)
        db.commit = AsyncMock()
        session_factory.return_value.__aenter__.return_value = db
        response = client.post("/v2/popia/deletion-execute/00000000-0000-0000-0000-000000000001")
    assert response.status_code == 202
    job = client.get(f"/v2/jobs/{response.json()['data']['job_id']}")
    assert job.status_code == 200
    assert job.json()["data"]["status"] == "completed"
    assert job.json()["data"]["result"]["purged"] is True


def test_rlhf_export_job_flow():
    client = _client()
    with patch("app.api_v2_routers.popia.enqueue_job", side_effect=_mock_enqueue):
        response = client.post("/v2/popia/rlhf-export/openai", json={"records": [{"prompt": "Hi", "chosen": "Hello"}]})
    assert response.status_code == 202
    job = client.get(f"/v2/jobs/{response.json()['data']['job_id']}")
    assert job.status_code == 200
    assert job.json()["data"]["status"] == "completed"
    assert job.json()["data"]["result"]["format"] == "openai"


def test_consent_renewal_job_flow():
    client = _client()
    with patch("app.core.database.AsyncSessionLocal") as session_factory, \
         patch("app.api_v2_routers.consent_renewal.enqueue_job", side_effect=_mock_enqueue), \
         patch("app.api_v2_routers.consent_renewal.ConsentRenewalService.run", new=AsyncMock(return_value={"checked": 1, "reminded": 1, "failed": 0, "skipped_already_expired": 0})), \
         patch("app.api_v2_routers.consent_renewal.SendGridEmailGateway"):
        db = AsyncMock()
        session_factory.return_value.__aenter__.return_value = db
        response = client.post("/v2/admin/consent/trigger-renewal-reminders")
    assert response.status_code == 202
    job = client.get(f"/v2/jobs/{response.json()['data']['job_id']}")
    assert job.status_code == 200
    assert job.json()["data"]["status"] == "completed"
    assert job.json()["data"]["result"]["reminded"] == 1
