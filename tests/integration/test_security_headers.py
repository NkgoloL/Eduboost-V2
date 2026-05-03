"""Test security headers middleware."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.api_v2 import app


@pytest.mark.asyncio
async def test_security_headers_present():
    """Test that all security headers are present on responses."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")  # Assuming health endpoint exists

        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("Strict-Transport-Security") == "max-age=63072000; includeSubDomains"
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert response.headers.get("Content-Security-Policy") == "default-src 'self'; script-src 'self'; object-src 'none'"