from __future__ import annotations

from starlette.responses import Response

from app.api_v2_routers.auth import REFRESH_COOKIE, _set_refresh_cookie


def test_refresh_cookie_is_http_only_secure_strict_and_scoped() -> None:
    response = Response()

    _set_refresh_cookie(response, "refresh-token-value")

    cookie = response.headers["set-cookie"]
    assert f"{REFRESH_COOKIE}=refresh-token-value" in cookie
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=strict" in cookie
    assert "Path=/api/v2/auth" in cookie
    assert "Max-Age=604800" in cookie
