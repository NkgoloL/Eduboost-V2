from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "study_plans.py"


@pytest.mark.unit
def test_study_plan_route_imports_consent_gate_and_db_dependency() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "from sqlalchemy.ext.asyncio import AsyncSession" in source
    assert "from app.core.database import AsyncSessionLocal, get_db" in source
    assert "require_active_consent_for_current_user" in source
    assert "db: AsyncSession = Depends(get_db)" in source


@pytest.mark.unit
def test_study_plan_route_calls_write_authz_then_active_consent() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "require_learner_write_for_current_user(current_user, learner_id)" in source
    assert "await require_active_consent_for_current_user(db, current_user, learner_id)" in source

    write_index = source.index("require_learner_write_for_current_user(current_user, learner_id)")
    consent_index = source.index("await require_active_consent_for_current_user(db, current_user, learner_id)")
    assert write_index < consent_index
