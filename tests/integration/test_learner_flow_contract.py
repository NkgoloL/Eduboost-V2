from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration


import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from app.api_v2 import app
from app.core.config import settings
from app.core.jobs import enqueue_job, run_job, create_job
from unittest.mock import patch


async def _poll_job(client: AsyncClient, token: str, job_id: str) -> dict:
    for _ in range(20):
        response = await client.get(
            f"/api/v2/jobs/{job_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        payload = response.json()["data"]
        if payload["status"] in {"completed", "failed"}:
            return payload
        await asyncio.sleep(0.05)
    raise AssertionError(f"Job {job_id} did not finish")


async def _mock_enqueue(background_tasks, *, operation, handler, payload=None):
    job = await create_job(operation, payload=payload)
    await run_job(job["job_id"], handler)
    return job


@pytest.mark.asyncio
@pytest.mark.integration
async def test_local_learner_flow_contract(monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")

    with patch("app.api_v2_routers.study_plans.enqueue_job", side_effect=_mock_enqueue), \
         patch("app.api_v2_routers.lessons.enqueue_job", side_effect=_mock_enqueue):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            session_response = await client.post("/api/v2/auth/dev-session")
            assert session_response.status_code == 200
            session = session_response.json()["data"]
            token = session["access_token"]
            learner_id = session["learner"]["learner_id"]
            auth = {"Authorization": f"Bearer {token}"}

            mastery_response = await client.get(f"/api/v2/learners/{learner_id}/mastery", headers=auth)
            assert mastery_response.status_code == 200
            assert mastery_response.json()["data"]["mastery"]

            profile_response = await client.get(f"/api/v2/gamification/profile/{learner_id}", headers=auth)
            assert profile_response.status_code == 200
            initial_xp = profile_response.json()["data"]["total_xp"]

            plan_response = await client.post(
                f"/api/v2/study-plans/generate/{learner_id}",
                headers=auth,
                json={"gap_ratio": 0.4},
            )
            assert plan_response.status_code == 202
            plan_job = await _poll_job(client, token, plan_response.json()["data"]["job_id"])
            assert plan_job["status"] == "completed"
            assert plan_job["result"]["days"]["Mon"]

            lesson_response = await client.post(
                "/api/v2/lessons/generate",
                headers=auth,
                json={"learner_id": learner_id, "subject": "MATH", "topic": "Fractions", "language": "en"},
            )
            assert lesson_response.status_code == 202
            lesson_job = await _poll_job(client, token, lesson_response.json()["data"]["job_id"])
            assert lesson_job["status"] == "completed"
            lesson_id = lesson_job["result"]["id"]

            complete_response = await client.post(f"/api/v2/lessons/{lesson_id}/complete", headers=auth)
            assert complete_response.status_code == 200

            award_response = await client.post(
                "/api/v2/gamification/award-xp",
                headers=auth,
                json={
                    "learner_id": learner_id,
                    "xp_amount": 35,
                    "event_type": "lesson_completed",
                    "lesson_id": lesson_id,
                },
            )
            assert award_response.status_code == 200
            award = award_response.json()["data"]
            assert award["awarded"] is True
            assert award["lesson_completed"] is True
            assert award["profile"]["total_xp"] == initial_xp + 35
