import uuid

import pytest

from app.models.content_factory import ContentArtifactStatus
from app.services.content_artifact_lifecycle import ContentArtifactLifecycleService


class Artifact:
    def __init__(self, status: str = "generated") -> None:
        self.artifact_id = uuid.uuid4()
        self.status = status


class Report:
    passed = True
    errors: list[str] = []


class FakeFactory:
    def __init__(self, artifact: Artifact) -> None:
        self.artifact = artifact
        self.asserted = False

    async def get_artifact(self, session, artifact_id):
        return self.artifact

    async def validate_existing_artifact(self, session, artifact_id):
        return Report()

    async def assert_artifact_has_approved_sources(self, session, artifact_id):
        self.asserted = True


class Session:
    async def flush(self):
        return None

    def add(self, obj):
        pass


@pytest.mark.asyncio
async def test_submit_for_review_requires_validation_pass() -> None:
    artifact = Artifact("generated")
    service = ContentArtifactLifecycleService(FakeFactory(artifact))
    transition = await service.submit_for_review(Session(), artifact.artifact_id, "admin")
    assert transition.new_status == ContentArtifactStatus.PENDING_REVIEW.value
    assert artifact.status == ContentArtifactStatus.PENDING_REVIEW

