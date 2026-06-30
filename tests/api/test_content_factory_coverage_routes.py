from __future__ import annotations

from dataclasses import dataclass
import uuid

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers.content_factory import get_content_coverage_service
from app.core.security import get_current_user
from app.services.content_coverage_service import ContentCoverageService


pytestmark = pytest.mark.unit


def _client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


def _admin_user() -> dict[str, str]:
    return {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"}


def _parent_user() -> dict[str, str]:
    return {"sub": str(uuid.uuid4()), "role": "parent", "type": "access"}


class FakeItemRepo:
    async def get_coverage_summary(self, caps_refs: list[str] | None = None) -> dict[str, dict[str, int]]:
        return {
            "4.M.1.1": {"approved": 40, "ai_generated": 0, "human_reviewed": 0, "rejected": 0},
            "4.M.1.2": {"approved": 20, "ai_generated": 1, "human_reviewed": 0, "rejected": 1},
            "4.M.1.3": {"approved": 0, "ai_generated": 2, "human_reviewed": 1, "rejected": 0},
        }


@dataclass
class Lesson:
    review_status: str


class FakeLessonRepo:
    async def list_by_caps_ref(self, caps_ref: str, include_all_statuses: bool = False) -> list[Lesson]:
        assert include_all_statuses is True
        if caps_ref == "4.M.1.1":
            return [Lesson("approved") for _ in range(8)]
        if caps_ref == "4.M.1.2":
            return [Lesson("approved") for _ in range(4)] + [Lesson("ai_generated")]
        return []


def _coverage_service() -> ContentCoverageService:
    return ContentCoverageService(item_repo=FakeItemRepo(), lesson_repo=FakeLessonRepo())


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    app.dependency_overrides.clear()
    app.openapi_schema = None
    yield
    app.dependency_overrides.clear()
    app.openapi_schema = None


def test_content_factory_coverage_requires_authentication() -> None:
    response = _client().get("/api/v2/admin/content-factory/scopes/grade4_mathematics_en/coverage")

    assert response.status_code == 401


def test_content_factory_coverage_rejects_non_admin_user() -> None:
    app.dependency_overrides[get_current_user] = _parent_user

    response = _client().get("/api/v2/admin/content-factory/scopes/grade4_mathematics_en/coverage")

    assert response.status_code == 403


def test_admin_can_fetch_scope_coverage() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[get_content_coverage_service] = _coverage_service

    response = _client().get("/api/v2/admin/content-factory/scopes/grade4_mathematics_en/coverage")

    assert response.status_code == 200
    report = response.json()["data"]
    assert report["scope_id"] == "grade4_mathematics_en"
    assert report["summary"] == {
        "total_caps_refs": 3,
        "green_refs": 1,
        "amber_refs": 1,
        "red_refs": 1,
        "not_configured_refs": 0,
    }
    assert report["layers"]["diagnostic_items"]["target_total"] == 120
    assert report["layers"]["lessons"]["target_total"] == 24


def test_admin_can_fetch_caps_ref_coverage() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[get_content_coverage_service] = _coverage_service

    response = _client().get("/api/v2/admin/content-factory/scopes/grade4_mathematics_en/coverage/4.M.1.1")

    assert response.status_code == 200
    report = response.json()["data"]
    assert report["caps_ref"] == "4.M.1.1"
    assert report["layers"]["diagnostic_items"]["target"] == 40
    assert report["layers"]["diagnostic_items"]["status"] == "green"
    assert report["layers"]["lessons"]["target"] == 8
    assert report["layers"]["lessons"]["status"] == "green"


def test_admin_can_filter_coverage_layers() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[get_content_coverage_service] = _coverage_service

    response = _client().get(
        "/api/v2/admin/content-factory/scopes/grade4_mathematics_en/coverage",
        params={"layer": "diagnostic_items"},
    )

    assert response.status_code == 200
    report = response.json()["data"]
    assert list(report["layers"]) == ["diagnostic_items"]
    assert list(report["per_caps_ref"][0]["layers"]) == ["diagnostic_items"]


def test_unknown_scope_returns_404_for_coverage() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[get_content_coverage_service] = _coverage_service

    response = _client().get("/api/v2/admin/content-factory/scopes/unknown_scope/coverage")

    assert response.status_code == 404


def test_caps_ref_outside_scope_returns_404_for_coverage() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[get_content_coverage_service] = _coverage_service

    response = _client().get("/api/v2/admin/content-factory/scopes/grade4_mathematics_en/coverage/4.M.9.9")

    assert response.status_code == 404
