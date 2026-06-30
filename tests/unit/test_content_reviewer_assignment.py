from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest

from app.services.content_reviewer_assignment import ContentReviewerAssignmentService


class Result:
    def __init__(self, rows=None, one=None):
        self.rows = rows or []
        self.one = one
    def scalars(self):
        return self
    def all(self):
        return self.rows
    def scalar_one_or_none(self):
        return self.one


class Session:
    def __init__(self, artifact=None, assignments=None):
        self.artifact = artifact or SimpleNamespace(artifact_id=uuid.uuid4())
        self.assignments = assignments or []
        self.added = []
    async def get(self, model, key):
        return self.artifact
    async def execute(self, stmt):
        return Result(self.assignments, self.assignments[0] if self.assignments else None)
    def add(self, obj):
        self.added.append(obj)
    async def flush(self):
        return None


@pytest.mark.asyncio
async def test_assignment_creates_workload_entries() -> None:
    session = Session()
    assignment = await ContentReviewerAssignmentService().assign_artifact(session, session.artifact.artifact_id, "reviewer-1", "admin")

    assert assignment.assigned_to == "reviewer-1"
    assert session.added


@pytest.mark.asyncio
async def test_reviewer_workload_counts_open_assignments() -> None:
    assignments = [SimpleNamespace(assigned_to="reviewer-1", status="assigned", due_by=None), SimpleNamespace(assigned_to="reviewer-1", status="in_review", due_by=None)]
    workload = await ContentReviewerAssignmentService().get_reviewer_workload(Session(assignments=assignments), "reviewer-1")

    assert workload.assigned == 1
    assert workload.in_review == 1
    assert workload.total_open == 2
