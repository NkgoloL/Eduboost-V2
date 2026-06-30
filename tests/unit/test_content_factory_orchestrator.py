import pytest

from app.domain.content_coverage import ContentLayer
from app.services.content_factory_orchestrator import ContentFactoryOrchestrator, PIPELINE_STATES
from tests.unit.test_content_generation_runs import FakeRegistry, FakeSession
from app.services.content_generation_runs import ContentGenerationRunService


@pytest.mark.asyncio
async def test_orchestrator_creates_dry_run_plan_when_generation_disabled(monkeypatch) -> None:
    monkeypatch.setenv("CONTENT_FACTORY_GENERATION_ENABLED", "false")
    service = ContentGenerationRunService(FakeRegistry())
    plan = await ContentFactoryOrchestrator(service).create_dry_run_plan(FakeSession(), scope_id="grade4_mathematics_en", layers=[ContentLayer.LESSONS], requested_by="admin")
    assert plan.generation_enabled is False
    assert plan.dry_run is True
    assert plan.planned_states == PIPELINE_STATES
    assert plan.task_count == 2
