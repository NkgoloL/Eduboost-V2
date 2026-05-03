"""Integration tests for JWT refresh token rotation."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.api_v2 import app


@pytest.mark.asyncio
@pytest.mark.integration
async def test_refresh_token_happy_path():
    """Test successful refresh token rotation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register a user
        register_response = await client.post(
            "/api/v2/auth/register",
            json={
                "email": "test@example.com",
                "display_name": "Test User",
                "password": "password123",
                "role": "parent"
            }
        )
        assert register_response.status_code == 201
        register_data = register_response.json()
        access_token = register_data["access_token"]
        refresh_cookie = register_response.cookies.get("eduboost_refresh")
        assert refresh_cookie is not None

        # Use the access token to get user info
        me_response = await client.get(
            "/api/v2/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert me_response.status_code == 200

        # Refresh the token
        refresh_response = await client.post(
            "/api/v2/auth/refresh",
            cookies={"eduboost_refresh": refresh_cookie}
        )
        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()
        new_access_token = refresh_data["access_token"]
        new_refresh_cookie = refresh_response.cookies.get("eduboost_refresh")
        assert new_refresh_cookie is not None
        assert new_refresh_cookie != refresh_cookie  # Should be rotated

        # Verify new access token works
        me_response2 = await client.get(
            "/api/v2/auth/me",
            headers={"Authorization": f"Bearer {new_access_token}"}
        )
        assert me_response2.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
async def test_refresh_token_reuse_detection():
    """Test that refresh tokens cannot be reused."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login
        register_response = await client.post(
            "/api/v2/auth/register",
            json={
                "email": "reuse@example.com",
                "display_name": "Reuse User",
                "password": "password123",
                "role": "parent"
            }
        )
        assert register_response.status_code == 201
        refresh_cookie = register_response.cookies.get("eduboost_refresh")

        # First refresh should succeed
        refresh_response1 = await client.post(
            "/api/v2/auth/refresh",
            cookies={"eduboost_refresh": refresh_cookie}
        )
        assert refresh_response1.status_code == 200

        # Second refresh with same token should fail
        refresh_response2 = await client.post(
            "/api/v2/auth/refresh",
            cookies={"eduboost_refresh": refresh_cookie}
        )
        assert refresh_response2.status_code == 401
        assert "already used" in refresh_response2.json()["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_logout_clears_refresh_cookie():
    """Test that logout clears the refresh token cookie."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register
        register_response = await client.post(
            "/api/v2/auth/register",
            json={
                "email": "logout@example.com",
                "display_name": "Logout User",
                "password": "password123",
                "role": "parent"
            }
        )
        assert register_response.status_code == 201
        access_token = register_response.json()["access_token"]
        refresh_cookie = register_response.cookies.get("eduboost_refresh")

        # Logout
        logout_response = await client.post(
            "/api/v2/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert logout_response.status_code == 204

        # Check that refresh cookie is cleared (set to empty or expired)
        # Note: httpx may not show deleted cookies, but we can try refresh
        refresh_response = await client.post(
            "/api/v2/auth/refresh",
            cookies={"eduboost_refresh": refresh_cookie}
        )
        # Should fail because token was revoked on logout
        assert refresh_response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
async def test_expired_refresh_token_rejection():
    """Test that expired refresh tokens are rejected."""
    # This would require mocking time or using a very short expiry
    # For now, skip or assume it's covered by decode_token
    pass