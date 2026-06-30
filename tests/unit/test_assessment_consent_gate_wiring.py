from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "assessments.py"


@pytest.mark.unit
def test_assessment_attempt_imports_consent_gate_and_db_dependency() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "from sqlalchemy.ext.asyncio import AsyncSession" in source
    assert "from app.core.database import get_db" in source
    assert "require_active_consent_for_current_user" in source
    assert "db: AsyncSession = Depends(get_db)" in source


@pytest.mark.unit
def test_assessment_attempt_authorizes_before_consent_gate() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def submit_attempt", maxsplit=1)[1]

    assert "require_learner_write_for_current_user(current_user, request.learner_id)" in block
    assert "await require_active_consent_for_current_user(db, current_user, request.learner_id)" in block
    assert block.index("require_learner_write_for_current_user(current_user, request.learner_id)") < block.index(
        "await require_active_consent_for_current_user(db, current_user, request.learner_id)"
    )


@pytest.mark.unit
def test_assessment_list_remains_authenticated_catalog_boundary() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def list_assessments", maxsplit=1)[1].split("@router.post", maxsplit=1)[0]

    assert "Depends(require_auth_context)" in block
    assert "require_active_consent_for_current_user" not in block
