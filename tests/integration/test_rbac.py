import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from app.api_v2 import app

pytestmark = pytest.mark.integration

"""Integration tests for Role-Based Access Control (RBAC)."""

def get_unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"

@pytest.mark.asyncio
@pytest.mark.integration
async def test_parent_can_create_learner():
    """Test that parent role can create learners."""
    email = get_unique_email("parent")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register as parent
        register_response = await client.post(
            "/api/v2/auth/register",
            json={
                "email": email,
                "display_name": "Parent User",
                "password": "Complex_Pass_2026!",
                "role": "parent"
            }
        )
        assert register_response.status_code == 201
        # V2 API uses EnvelopedRoute, so we access through ["data"]
        access_token = register_response.json()["data"]["access_token"]

        # Create learner
        create_response = await client.post(
            "/api/v2/learners/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "display_name": "Test Learner",
                "grade": 3,
                "language": "en"
            }
        )
        assert create_response.status_code == 201

@pytest.mark.asyncio
@pytest.mark.integration
async def test_teacher_cannot_create_learner():
    """Test that teacher role cannot create learners (only parents/admins can)."""
    email = get_unique_email("teacher")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register as teacher
        register_response = await client.post(
            "/api/v2/auth/register",
            json={
                "email": email,
                "display_name": "Teacher User",
                "password": "Complex_Pass_2026!",
                "role": "teacher"
            }
        )
        assert register_response.status_code == 201
        access_token = register_response.json()["data"]["access_token"]

        # Try to create learner
        create_response = await client.post(
            "/api/v2/learners/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "display_name": "Test Learner",
                "grade": 3,
                "language": "en"
            }
        )
        # Should be 403 because learners belong to parents/admins
        assert create_response.status_code == 403

@pytest.mark.asyncio
@pytest.mark.integration
async def test_unauthorized_access_is_blocked():
    """Test that requests without valid tokens are blocked."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v2/auth/me")
        assert response.status_code == 401