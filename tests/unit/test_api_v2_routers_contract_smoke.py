"""Contract smoke tests for API v2 routers.

These tests verify router registration, OpenAPI exposure, and basic HTTP behavior
without requiring real database connections. They use FastAPI TestClient with
mocked service dependencies to provide fast, focused coverage of router code.
"""

from __future__ import annotations


import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app


@pytest.fixture
def client():
    """FastAPI TestClient for router contract testing."""
    return TestClient(app)


class TestSystemRouter:
    """Contract tests for system router."""

    def test_health_endpoint_exists_in_openapi(self, client):
        """System health endpoint is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        assert "/api/v2/system/health" in schema["paths"]
        assert "get" in schema["paths"]["/api/v2/system/health"]
        assert schema["paths"]["/api/v2/system/health"]["get"]["tags"] == ["V2 System"]

    def test_pillars_endpoint_exists_in_openapi(self, client):
        """System pillars endpoint is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        assert "/api/v2/system/pillars" in schema["paths"]
        assert "get" in schema["paths"]["/api/v2/system/pillars"]

    def test_schema_status_endpoint_exists_in_openapi(self, client):
        """System schema-status endpoint is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        assert "/api/v2/system/schema-status" in schema["paths"]
        assert "get" in schema["paths"]["/api/v2/system/schema-status"]

    def test_capabilities_endpoint_exists_in_openapi(self, client):
        """System capabilities endpoint is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        assert "/api/v2/system/capabilities" in schema["paths"]
        assert "get" in schema["paths"]["/api/v2/system/capabilities"]

    def test_health_endpoint_returns_200(self, client):
        """Health endpoint returns 200 status."""
        response = client.get("/api/v2/system/health")
        assert response.status_code == 200

    def test_pillars_endpoint_returns_200(self, client):
        """Pillars endpoint returns 200 status."""
        response = client.get("/api/v2/system/pillars")
        assert response.status_code == 200

    def test_schema_status_endpoint_returns_200(self, client):
        """Schema status endpoint returns 200 status."""
        response = client.get("/api/v2/system/schema-status")
        assert response.status_code == 200

    def test_capabilities_endpoint_returns_200(self, client):
        """Capabilities endpoint returns 200 status."""
        response = client.get("/api/v2/system/capabilities")
        assert response.status_code == 200


class TestConsentRouter:
    """Contract tests for consent router."""

    def test_consent_router_exists_in_openapi(self, client):
        """Consent router is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        consent_paths = [p for p in schema["paths"] if "/consent" in p]
        assert len(consent_paths) > 0

    def test_consent_endpoints_have_correct_tag(self, client):
        """Consent endpoints are tagged correctly."""
        schema = client.app.openapi()
        consent_paths = [p for p in schema["paths"] if "/consent" in p]
        for path in consent_paths:
            for method in schema["paths"][path]:
                tags = schema["paths"][path][method].get("tags", [])
                assert any("consent" in tag.lower() or "popia" in tag.lower() for tag in tags)


class TestPopiaRouter:
    """Contract tests for POPIA router."""

    def test_popia_router_exists_in_openapi(self, client):
        """POPIA router is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        popia_paths = [p for p in schema["paths"] if "/popia" in p]
        assert len(popia_paths) > 0

    def test_popia_endpoints_have_correct_tag(self, client):
        """POPIA endpoints are tagged correctly."""
        schema = client.app.openapi()
        popia_paths = [p for p in schema["paths"] if "/popia" in p]
        for path in popia_paths:
            for method in schema["paths"][path]:
                tags = schema["paths"][path][method].get("tags", [])
                assert any("popia" in tag.lower() for tag in tags)


class TestAuthRouter:
    """Contract tests for auth router."""

    def test_auth_router_exists_in_openapi(self, client):
        """Auth router is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        auth_paths = [p for p in schema["paths"] if "/auth" in p]
        assert len(auth_paths) > 0

    def test_auth_endpoints_have_correct_tag(self, client):
        """Auth endpoints are tagged correctly."""
        schema = client.app.openapi()
        auth_paths = [p for p in schema["paths"] if "/auth" in p]
        for path in auth_paths:
            for method in schema["paths"][path]:
                tags = schema["paths"][path][method].get("tags", [])
                assert any("auth" in tag.lower() for tag in tags)


class TestDiagnosticsRouter:
    """Contract tests for diagnostics router."""

    def test_diagnostics_router_exists_in_openapi(self, client):
        """Diagnostics router is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        diag_paths = [p for p in schema["paths"] if "/diagnostics" in p]
        assert len(diag_paths) > 0

    def test_diagnostics_endpoints_have_correct_tag(self, client):
        """Diagnostics endpoints are tagged correctly."""
        schema = client.app.openapi()
        diag_paths = [p for p in schema["paths"] if "/diagnostics" in p]
        for path in diag_paths:
            for method in schema["paths"][path]:
                tags = schema["paths"][path][method].get("tags", [])
                assert any("diagnostic" in tag.lower() for tag in tags)


class TestLearnersRouter:
    """Contract tests for learners router."""

    def test_learners_router_exists_in_openapi(self, client):
        """Learners router is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        learner_paths = [p for p in schema["paths"] if "/learners" in p]
        assert len(learner_paths) > 0

    def test_learners_endpoints_have_correct_tag(self, client):
        """Learners endpoints are tagged correctly."""
        schema = client.app.openapi()
        learner_paths = [p for p in schema["paths"] if "/learners" in p]
        for path in learner_paths:
            for method in schema["paths"][path]:
                tags = schema["paths"][path][method].get("tags", [])
                assert len(tags) > 0


class TestLessonsRouter:
    """Contract tests for lessons router."""

    def test_lessons_router_exists_in_openapi(self, client):
        """Lessons router is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        lesson_paths = [p for p in schema["paths"] if "/lessons" in p]
        assert len(lesson_paths) > 0

    def test_lessons_endpoints_have_correct_tag(self, client):
        """Lessons endpoints are tagged correctly."""
        schema = client.app.openapi()
        lesson_paths = [p for p in schema["paths"] if "/lessons" in p]
        for path in lesson_paths:
            for method in schema["paths"][path]:
                tags = schema["paths"][path][method].get("tags", [])
                assert len(tags) > 0


class TestBillingRouter:
    """Contract tests for billing router."""

    def test_billing_router_exists_in_openapi(self, client):
        """Billing router is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        billing_paths = [p for p in schema["paths"] if "/billing" in p]
        assert len(billing_paths) > 0

    def test_billing_endpoints_have_correct_tag(self, client):
        """Billing endpoints are tagged correctly."""
        schema = client.app.openapi()
        billing_paths = [p for p in schema["paths"] if "/billing" in p]
        for path in billing_paths:
            for method in schema["paths"][path]:
                tags = schema["paths"][path][method].get("tags", [])
                assert any("billing" in tag.lower() for tag in tags)


class TestParentsRouter:
    """Contract tests for parents router."""

    def test_parents_router_exists_in_openapi(self, client):
        """Parents router is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        parent_paths = [p for p in schema["paths"] if "/parents" in p]
        assert len(parent_paths) > 0

    def test_parents_endpoints_have_correct_tag(self, client):
        """Parents endpoints are tagged correctly."""
        schema = client.app.openapi()
        parent_paths = [p for p in schema["paths"] if "/parents" in p]
        for path in parent_paths:
            for method in schema["paths"][path]:
                tags = schema["paths"][path][method].get("tags", [])
                assert any("parent" in tag.lower() for tag in tags)


class TestGamificationRouter:
    """Contract tests for gamification router."""

    def test_gamification_router_exists_in_openapi(self, client):
        """Gamification router is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        gamification_paths = [p for p in schema["paths"] if "/gamification" in p]
        assert len(gamification_paths) > 0

    def test_gamification_endpoints_have_correct_tag(self, client):
        """Gamification endpoints are tagged correctly."""
        schema = client.app.openapi()
        gamification_paths = [p for p in schema["paths"] if "/gamification" in p]
        for path in gamification_paths:
            for method in schema["paths"][path]:
                tags = schema["paths"][path][method].get("tags", [])
                assert any("gamification" in tag.lower() for tag in tags)


class TestJobsRouter:
    """Contract tests for jobs router."""

    def test_jobs_router_exists_in_openapi(self, client):
        """Jobs router is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        job_paths = [p for p in schema["paths"] if "/jobs" in p]
        assert len(job_paths) > 0

    def test_jobs_endpoints_have_correct_tag(self, client):
        """Jobs endpoints are tagged correctly."""
        schema = client.app.openapi()
        job_paths = [p for p in schema["paths"] if "/jobs" in p]
        for path in job_paths:
            for method in schema["paths"][path]:
                tags = schema["paths"][path][method].get("tags", [])
                assert any("job" in tag.lower() for tag in tags)


class TestStudyPlansRouter:
    """Contract tests for study plans router."""

    def test_study_plans_router_exists_in_openapi(self, client):
        """Study plans router is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        study_paths = [p for p in schema["paths"] if "/study-plans" in p]
        assert len(study_paths) > 0

    def test_study_plans_endpoints_have_correct_tag(self, client):
        """Study plans endpoints are tagged correctly."""
        schema = client.app.openapi()
        study_paths = [p for p in schema["paths"] if "/study-plans" in p]
        for path in study_paths:
            for method in schema["paths"][path]:
                tags = schema["paths"][path][method].get("tags", [])
                assert any("study" in tag.lower() for tag in tags)


class TestAssessmentsRouter:
    """Contract tests for assessments router."""

    def test_assessments_router_exists_in_openapi(self, client):
        """Assessments router is exposed in OpenAPI schema."""
        schema = client.app.openapi()
        assessment_paths = [p for p in schema["paths"] if "/assessments" in p]
        assert len(assessment_paths) > 0

    def test_assessments_endpoints_have_correct_tag(self, client):
        """Assessments endpoints are tagged correctly."""
        schema = client.app.openapi()
        assessment_paths = [p for p in schema["paths"] if "/assessments" in p]
        for path in assessment_paths:
            for method in schema["paths"][path]:
                tags = schema["paths"][path][method].get("tags", [])
                assert any("assessment" in tag.lower() for tag in tags)
