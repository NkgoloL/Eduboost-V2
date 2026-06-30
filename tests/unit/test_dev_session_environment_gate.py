from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUTH_ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "auth.py"


@pytest.mark.unit
def test_dev_session_has_production_404_gate() -> None:
    source = AUTH_ROUTER.read_text(encoding="utf-8")
    block = source.split("async def create_dev_session", maxsplit=1)[1].split("@router.post(\"/refresh\"", maxsplit=1)[0]

    assert "settings.is_production()" in block
    assert "status.HTTP_404_NOT_FOUND" in block
    assert "Not found" in block


@pytest.mark.unit
def test_dev_session_is_documented_as_non_production_bootstrap() -> None:
    source = AUTH_ROUTER.read_text(encoding="utf-8")
    block = source.split("async def create_dev_session", maxsplit=1)[1].split("@router.post(\"/refresh\"", maxsplit=1)[0]

    assert "Non-production bootstrap endpoint" in block
    assert "DEV_SESSION_BOOTSTRAPPED" in block
