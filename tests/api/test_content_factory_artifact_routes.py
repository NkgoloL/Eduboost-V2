import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import content_factory
from app.core.security import get_current_user

pytestmark = pytest.mark.unit


class Source:
    source_document_id = "doc"
    source_chunk_id = "chunk"
    curriculum_mapping_id = None
    source_hash = "hash"
    source_role = "primary_context"
    source_metadata = {"document_status": "approved"}


class Artifact:
    def __init__(self):
        self.artifact_id = uuid.uuid4()
        self.scope_id = "grade4_mathematics_en"
        self.content_layer = "lessons"
        self.artifact_type = "lesson"
        self.caps_ref = "4.M.1.1"
        self.status = "pending_review"
        self.artifact_hash = "sha256:x"
        self.source_snapshot_hash = "sha256:s"
        self.sources = [Source()]


class FakeFactory:
    def __init__(self):
        self.artifact = Artifact()

    async def get_artifact(self, session, artifact_id):
        return self.artifact


class FakeLifecycle:
    async def submit_for_review(self, session, artifact_id, actor_id):
        return SimpleNamespace(artifact_id=artifact_id, previous_status="generated", new_status="pending_review", actor_id=actor_id, reason=None)

    async def reject_artifact(self, session, artifact_id, actor_id, reason):
        return SimpleNamespace(artifact_id=artifact_id, previous_status="pending_review", new_status="rejected", actor_id=actor_id, reason=reason)

    async def quarantine_artifact(self, session, artifact_id, actor_id, reason):
        return SimpleNamespace(artifact_id=artifact_id, previous_status="pending_review", new_status="quarantined", actor_id=actor_id, reason=reason)


class FakeSession:
    async def commit(self):
        return None

    async def execute(self, stmt):
        class R:
            def scalars(self):
                return self
            def all(self):
                return [Artifact()]
        return R()


def _admin_user():
    return {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"}


def _fake_session():
    return FakeSession()


def _fake_factory():
    return FakeFactory()


def _fake_lifecycle():
    return FakeLifecycle()


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear()
    app.openapi_schema = None
    yield
    app.dependency_overrides.clear()
    app.openapi_schema = None


def test_admin_can_fetch_provenance() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _fake_session
    app.dependency_overrides[content_factory.get_content_factory_service] = _fake_factory
    response = TestClient(app, raise_server_exceptions=False).get(f"/api/v2/admin/content-factory/artifacts/{uuid.uuid4()}/provenance")
    assert response.status_code == 200
    assert response.json()["data"]["sources"][0]["source_document_id"] == "doc"
