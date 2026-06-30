from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.core.jobs import create_job, get_job
from app.modules import jobs as worker_jobs


class _AsyncSessionFactory:
    def __init__(self, db: object) -> None:
        self._db = db

    def __call__(self):
        return self

    async def __aenter__(self):
        return self._db

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeArqPool:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def enqueue_job(self, function_name, *args, _job_id=None, **kwargs):
        self.calls.append(
            {
                "function_name": function_name,
                "args": args,
                "job_id": _job_id,
                "kwargs": kwargs,
            }
        )
        return SimpleNamespace(job_id=_job_id)


@pytest.mark.asyncio
async def test_enqueue_durable_returns_job_id_and_calls_arq_pool():
    pool = _FakeArqPool()
    with patch("app.modules.jobs._get_arq_pool", new=AsyncMock(return_value=pool)):
        job_id = await worker_jobs.enqueue_durable(
            "generate_lesson_job",
            operation="lesson_generation",
            payload={"learner_id": "learner-1", "subject": "Mathematics", "topic": "Fractions"},
            kwargs={
                "learner_id": "learner-1",
                "subject": "Mathematics",
                "topic": "Fractions",
                "language": "en",
                "current_user_id": "00000000-0000-0000-0000-000000000002",
            },
        )

    assert isinstance(job_id, str)
    assert pool.calls[0]["function_name"] == "generate_lesson_job"
    assert pool.calls[0]["job_id"] == job_id
    assert pool.calls[0]["kwargs"]["job_id"] == job_id

    job = await get_job(job_id)
    assert job is not None
    assert job["status"] == "queued"
    assert job["operation"] == "lesson_generation"


@pytest.mark.asyncio
async def test_generate_lesson_job_updates_status_and_result():
    job = await create_job(
        "lesson_generation",
        payload={
            "learner_id": "learner-1",
            "subject": "Mathematics",
            "topic": "Fractions",
            "language": "en",
            "current_user_id": "00000000-0000-0000-0000-000000000002",
        },
    )
    fake_lesson = SimpleNamespace(
        model_dump=lambda mode="json": {"id": "lesson-1", "subject": "Mathematics"},
    )
    fake_db = object()

    with patch("app.core.database.AsyncSessionLocal", new=_AsyncSessionFactory(fake_db)), \
         patch("app.modules.lessons.service.LessonService.generate_lesson_for_learner", new=AsyncMock(return_value=(fake_lesson, False, "openai"))):
        result = await worker_jobs.generate_lesson_job(
            {},
            job_id=job["job_id"],
            learner_id="learner-1",
            subject="Mathematics",
            topic="Fractions",
            language="en",
            current_user_id="00000000-0000-0000-0000-000000000002",
        )

    assert result["lesson"]["id"] == "lesson-1"
    status = await get_job(job["job_id"])
    assert status is not None
    assert status["status"] == "completed"
    assert status["result"]["lesson"]["id"] == "lesson-1"


@pytest.mark.asyncio
async def test_generate_study_plan_job_updates_status_and_result():
    job = await create_job(
        "study_plan_generation",
        payload={"learner_id": "learner-1", "gap_ratio": 0.4},
    )
    fake_db = object()
    fake_service = AsyncMock()
    fake_service.generate_plan = AsyncMock(return_value={"plan_id": "plan-1", "learner_id": "learner-1"})

    with patch("app.core.database.AsyncSessionLocal", new=_AsyncSessionFactory(fake_db)), \
         patch("app.repositories.repositories.LearnerRepository", new=lambda db: object()), \
         patch("app.repositories.study_plan_repository.StudyPlanRepository", new=lambda: object()), \
         patch("app.services.study_plan_service_v2.StudyPlanServiceV2", new=lambda *args, **kwargs: fake_service), \
         patch("app.services.audit_service.AuditService.log_event", new=AsyncMock()), \
         patch("app.services.telemetry.TelemetryService.track_event_async", new=AsyncMock()):
        result = await worker_jobs.generate_study_plan_job(
            {},
            job_id=job["job_id"],
            learner_id="learner-1",
            gap_ratio=0.4,
        )

    assert result["plan_id"] == "plan-1"
    status = await get_job(job["job_id"])
    assert status is not None
    assert status["status"] == "completed"
    assert status["result"]["plan_id"] == "plan-1"


@pytest.mark.asyncio
async def test_consent_renewal_job_updates_status_and_result():
    job = await create_job("consent_renewal_reminders", payload={})

    with patch("app.modules.jobs.run_consent_reminder_cycle", new=AsyncMock()):
        result = await worker_jobs.send_consent_renewal_reminders(
            {},
            job_id=job["job_id"],
        )

    assert result["status"] == "sent"
    status = await get_job(job["job_id"])
    assert status is not None
    assert status["status"] == "completed"
    assert status["result"]["status"] == "sent"


@pytest.mark.asyncio
async def test_consent_renewal_job_ignores_runtime_objects_in_ctx():
    class SessionEventsDispatch:
        pass

    job = await create_job("consent_renewal_reminders", payload={})

    with patch("app.modules.jobs.run_consent_reminder_cycle", new=AsyncMock()) as reminder_cycle:
        result = await worker_jobs.send_consent_renewal_reminders(
            {"dispatch": SessionEventsDispatch()},
            job_id=job["job_id"],
        )

    assert result["status"] == "sent"
    reminder_cycle.assert_awaited_once()
    status = await get_job(job["job_id"])
    assert status is not None
    assert status["status"] == "completed"
