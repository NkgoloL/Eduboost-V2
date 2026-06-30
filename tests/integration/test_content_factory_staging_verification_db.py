from __future__ import annotations

import pytest
from sqlalchemy import select

from app.models.content_factory import ContentStagingVerificationRun, ContentStagingVerificationScopeResult
from app.services.content_staging_readiness import ContentStagingReadinessService

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_staging_verification_report_is_persisted(db_session):
    service = ContentStagingReadinessService()

    report = await service.verify_all_scopes(db_session, actor_id="admin-1")
    await db_session.flush()

    assert report.run_id is not None
    run = (await db_session.execute(select(ContentStagingVerificationRun).where(ContentStagingVerificationRun.run_id == report.run_id))).scalar_one()
    assert run.created_by == "admin-1"
    result = (await db_session.execute(select(ContentStagingVerificationScopeResult).where(ContentStagingVerificationScopeResult.run_id == report.run_id))).scalar_one()
    assert result.scope_id == "grade4_mathematics_en"
    assert result.blockers_json
