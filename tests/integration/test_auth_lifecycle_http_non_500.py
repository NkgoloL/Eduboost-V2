from __future__ import annotations

from fastapi.testclient import TestClient


def _client():
    try:
        from app.api_v2 import app
    except Exception:
        from app.main import app  # type: ignore
    return TestClient(app, raise_server_exceptions=False)


def _paths():
    client = _client()
    return {getattr(route, "path", "") for route in client.app.routes}


def _first_matching(*needles: str) -> str:
    for path in sorted(_paths()):
        lowered = path.lower()
        if all(needle in lowered for needle in needles):
            return path
    raise AssertionError(f"No route path contains {needles!r}")


def test_register_http_path_does_not_500_on_invalid_payload():
    response = _client().post(_first_matching("register"), json={})
    assert response.status_code < 500


def test_login_http_path_does_not_500_on_invalid_payload():
    response = _client().post(_first_matching("login"), json={})
    assert response.status_code < 500


def test_refresh_http_path_does_not_500_on_invalid_payload():
    response = _client().post(_first_matching("refresh"), json={})
    assert response.status_code < 500
