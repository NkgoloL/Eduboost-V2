from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest

from app.models.content_factory import ContentGenerationRun
from app.services.content_generation.source_context import SourceContextResult
from app.services.content_generation.prompt_payloads import SourceContextChunk
from app.services.content_generation_planner import ContentGenerationPlanner
from app.services.content_staging_readiness import LayerReadinessSummary, ScopeStagingVerificationReport, StagingReadinessStatus


class Result:
    def __init__(self, row=None):
        self.row = row
    def scalar_one_or_none(self):
        return self.row


class Session:
    def __init__(self, run, duplicate=None):
        self.run = run
        self.duplicate = duplicate
        self.added = []
    async def get(self, model, key):
        return self.run
    async def execute(self, stmt):
        return Result(self.duplicate)
    def add(self, obj):
        self.added.append(obj)
    async def flush(self):
        return None


class Registry:
    def __init__(self):
        self.scope = SimpleNamespace(scope_id="grade4_mathematics_en", grade=4, subject_code="MAT", language="en", caps_refs=["4.M.1.1"])
    def list_scopes(self):
        return [self.scope]
    def get_scope(self, scope_id):
        return self.scope


class Readiness:
    def __init__(self, status=StagingReadinessStatus.PARTIALLY_STAGEABLE, approved=1, target=3):
        self.status = status
        self.approved = approved
        self.target = target
    async def verify_scope(self, scope_id, *, session, include_partial=True):
        layer = LayerReadinessSummary(layer="diagnostic_items", caps_ref="4.M.1.1", target=self.target, approved=self.approved, stageable=self.approved, status=self.status)
        return ScopeStagingVerificationReport(scope_id=scope_id, status=self.status, can_seed_staging=True, can_promote_production=False, layers=[layer])


class Sources:
    def __init__(self, passed=True):
        self.passed = passed
    async def build_context(self, session, *, scope_id, caps_ref, limit=8):
        return SourceContextResult(self.passed, [] if self.passed else ["missing"], [SourceContextChunk(source_document_id="doc", source_chunk_id="chunk", text="text")])


def _run():
    return ContentGenerationRun(run_id=uuid.uuid4(), scope_id="grade4_mathematics_en", requested_by="admin", status="created", run_metadata={})


@pytest.mark.asyncio
async def test_planner_creates_tasks_only_for_missing_targets(monkeypatch) -> None:
    monkeypatch.setenv("CONTENT_FACTORY_MAX_ARTIFACTS_PER_TASK", "10")
    run = _run()
    session = Session(run)
    result = await ContentGenerationPlanner(scope_registry=Registry(), readiness_service=Readiness(), source_context_service=Sources()).plan_missing_for_run(session, run.run_id)

    assert len(result.created_task_ids) == 1
    assert session.added[0].task_metadata["missing_count"] == 2


@pytest.mark.asyncio
async def test_planner_skips_fully_green_caps_refs() -> None:
    run = _run()
    session = Session(run)
    result = await ContentGenerationPlanner(scope_registry=Registry(), readiness_service=Readiness(StagingReadinessStatus.READY_FOR_STAGING, approved=3, target=3), source_context_service=Sources()).plan_missing_for_run(session, run.run_id)

    assert result.created_task_ids == []
    assert result.skipped[0]["reason"] == "coverage_green"


@pytest.mark.asyncio
async def test_planner_skips_missing_etl_source_context() -> None:
    run = _run()
    session = Session(run)
    result = await ContentGenerationPlanner(scope_registry=Registry(), readiness_service=Readiness(), source_context_service=Sources(False)).plan_missing_for_run(session, run.run_id)

    assert result.created_task_ids == []
    assert result.skipped[0]["reason"] == "missing_source_context"


@pytest.mark.asyncio
async def test_planner_idempotency_prevents_duplicate_tasks() -> None:
    run = _run()
    session = Session(run, duplicate=object())
    result = await ContentGenerationPlanner(scope_registry=Registry(), readiness_service=Readiness(), source_context_service=Sources()).plan_missing_for_run(session, run.run_id)

    assert result.created_task_ids == []
    assert result.skipped[0]["reason"] == "duplicate_task"
