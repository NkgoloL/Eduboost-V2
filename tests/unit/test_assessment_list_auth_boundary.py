"""Tests for assessment list authentication boundary."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_assessment_list_requires_authenticated_user() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "assessments.py").read_text(encoding="utf-8")
    block = source.split("async def list_assessments", maxsplit=1)[1].split("@router.post", maxsplit=1)[0]

    assert "_: AuthContext = Depends(require_auth_context)" in block
    assert "from app.api_v2_deps.auth import AuthContext, require_auth_context" in source
