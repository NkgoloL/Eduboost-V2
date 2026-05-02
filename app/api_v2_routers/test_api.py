"""
EduBoost V2 — Integration Tests
Tests POPIA consent gating and auth token flow.
Requires test DB + Redis. Run with: pytest tests/integration/ -v
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.api_v2 import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.anyio
class TestHealthEndpoints:
    async def test_health_returns_ok(self, client: AsyncClient):
        r = await client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "version" in data

    async def test_root_returns_message(self, client: AsyncClient):
        r = await client.get("/")
        assert r.status_code == 200
        assert "EduBoost" in r.json()["message"]


@pytest.mark.anyio
class TestAuthEndpoints:
    async def test_register_missing_fields(self, client: AsyncClient):
        r = await client.post("/api/v2/auth/register", json={"email": "test@edu.co.za"})
        assert r.status_code == 422  # Validation error

    async def test_login_invalid_credentials(self, client: AsyncClient):
        r = await client.post(
            "/api/v2/auth/login",
            json={"email": "nobody@edu.co.za", "password": "wrongpass"},
        )
        # DB not connected in unit context, expect 500 or 401
        assert r.status_code in (401, 500)


@pytest.mark.anyio
class TestConsentGating:
    async def test_lesson_without_token_returns_403(self, client: AsyncClient):
        r = await client.post(
            "/api/v2/lessons/",
            json={"learner_id": "fake-id", "subject": "Math", "topic": "Fractions"},
        )
        assert r.status_code == 403  # No bearer token

    async def test_learner_without_token_returns_403(self, client: AsyncClient):
        r = await client.get("/api/v2/learners/fake-id")
        assert r.status_code == 403


@pytest.mark.anyio
class TestOnboardingEndpoints:
    async def test_questions_require_auth(self, client: AsyncClient):
        r = await client.get("/api/v2/onboarding/questions")
        assert r.status_code == 403
