from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
DEPENDENCIES = REPO_ROOT / "app" / "security" / "dependencies.py"


@pytest.mark.unit
def test_consent_dependency_adapter_exists() -> None:
    source = DEPENDENCIES.read_text(encoding="utf-8")

    assert "def actor_id_from_current_user" in source
    assert "async def require_active_consent_for_current_user" in source
    assert "ConsentService(db).require_active_consent" in source


@pytest.mark.unit
def test_consent_dependency_adapter_preserves_authorization_concept_boundary() -> None:
    source = DEPENDENCIES.read_text(encoding="utf-8")
    block = source.split("async def require_active_consent_for_current_user", maxsplit=1)[1]

    assert "Authorization answers" in block
    assert "Consent answers" in block
    assert "actor_id=actor_id_from_current_user(current_user)" in block
