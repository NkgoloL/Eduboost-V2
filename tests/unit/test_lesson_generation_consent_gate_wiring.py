from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "lessons.py"


@pytest.mark.unit
def test_lesson_routes_import_consent_gate_adapter() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "require_active_consent_for_current_user" in source


@pytest.mark.unit
def test_lesson_generation_routes_call_consent_gate_after_write_authorization() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "require_learner_write_for_current_user" in source
    assert "await require_active_consent_for_current_user(db, auth" in source

    write_index = source.index("require_learner_write_for_current_user")
    consent_index = source.index("await require_active_consent_for_current_user")
    assert write_index < consent_index
