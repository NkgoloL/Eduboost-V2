"""Tests for lesson stream authorization wiring."""
from __future__ import annotations

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_lesson_stream_uses_phase2_write_authorization() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "lessons.py").read_text(encoding="utf-8")
    block = source.split("async def generate_lesson_stream", maxsplit=1)[1].split("return StreamingResponse", maxsplit=1)[0]
    assert "auth: AuthContext = Depends(require_auth_context)" in block
    assert "require_learner_write_for_current_user(auth, str(body.learner_id))" in block
    assert "user_id = UUID(str(auth.user_id))" in block
    assert "Depends(get_current_user)" not in block
