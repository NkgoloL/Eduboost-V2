from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.api_v2_routers.content_review import router
from app.domain.content_review_schemas import ReviewAssignmentCreateRequest


def test_phase3_router_exposes_expected_operations() -> None:
    paths = {route.path for route in router.routes}
    assert "/content-review/artifacts/{artifact_id}/assignments" in paths
    assert "/content-review/assignments/{assignment_id}/reassign" in paths
    assert "/content-review/artifacts/{artifact_id}/decisions" in paths
    assert "/content-review/artifacts/{artifact_id}/revisions" in paths
    assert "/content-review/artifacts/{artifact_id}/publish" in paths
    assert "/content-review/artifacts/{artifact_id}/history" in paths


def test_assignment_schema_rejects_duplicate_reviewers() -> None:
    with pytest.raises(ValidationError, match="distinct"):
        ReviewAssignmentCreateRequest(reviewer_ids=["r1", "r1"])
