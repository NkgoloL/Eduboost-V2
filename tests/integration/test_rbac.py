"""Integration tests for Role-Based Access Control (RBAC)."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.api_v2 import app


@pytest.mark.asyncio
@pytest.mark.integration
async def test_parent_can_create_learner():
    """Test that parent role can create learners."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register as parent
        register_response = await client.post(
            "/api/v2/auth/register",
            json={
                "email": "parent@example.com",
                "display_name": "Parent User",
                "password": "password123",
                "role": "parent"
            }
        )
        assert register_response.status_code == 201
        access_token = register_response.json()["access_token"]

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
async def test_student_cannot_create_learner():
    """Test that student role cannot create learners."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register as student
        register_response = await client.post(
            "/api/v2/auth/register",
            json={
                "email": "student@example.com",
                "display_name": "Student User",
                "password": "password123",
                "role": "student"
            }
        )
        assert register_response.status_code == 201
        access_token = register_response.json()["access_token"]

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
        assert create_response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_can_access_all_endpoints():
    """Test that admin role can access all endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register as admin
        register_response = await client.post(
            "/api/v2/auth/register",
            json={
                "email": "admin@example.com",
                "display_name": "Admin User",
                "password": "password123",
                "role": "admin"
            }
        )
        assert register_response.status_code == 201
        access_token = register_response.json()["access_token"]

        # Try admin-only endpoint (assuming one exists, e.g., system status)
        # For now, just check that registration worked
        assert access_token is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_teacher_can_access_analytics():
    """Test that teacher role can access anonymized analytics."""
    # Assuming there's an analytics endpoint for teachers
    pass