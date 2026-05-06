import pytest
from fastapi.testclient import TestClient
from app.api_v2 import app
from app.core.config import settings

client = TestClient(app)

@pytest.mark.parametrize("endpoint", [
    "/health",
    "/ready",
    "/openapi.json",
])
def test_security_headers_present(endpoint):
    response = client.get(endpoint)
    headers = response.headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-XSS-Protection"] == "1; mode=block"
    assert headers["Strict-Transport-Security"].startswith("max-age=")
    assert "Content-Security-Policy" in headers
    assert "Referrer-Policy" in headers
    assert "Permissions-Policy" in headers


def test_cors_headers_for_allowed_origin():
    allowed_origin = settings.ALLOWED_ORIGINS[0] if settings.ALLOWED_ORIGINS else "*"
    response = client.options(
        "/v2/auth/register",
        headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization,Content-Type",
        },
    )
    assert response.status_code in (200, 204)
    assert response.headers.get("Access-Control-Allow-Origin") in (allowed_origin, "*")
    assert response.headers.get("Access-Control-Allow-Methods") is not None
    assert response.headers.get("Access-Control-Allow-Headers") is not None


def test_cors_headers_for_disallowed_origin():
    disallowed_origin = "https://notallowed.example.com"
    response = client.options(
        "/health",
        headers={
            "Origin": disallowed_origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    # Should not echo disallowed origin
    assert response.headers.get("Access-Control-Allow-Origin") not in (disallowed_origin,)
