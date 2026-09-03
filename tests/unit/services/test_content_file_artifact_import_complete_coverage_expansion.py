import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentGenerationArtifact,
)
from app.services.content_file_artifact_import import (
    ContentFileArtifactImportService,
    FileArtifactImportRecord,
    FileArtifactImportPlan,
    _caps_ref_for,
)


def test_caps_ref_for_selection_rules_and_none():
    # 1. caps_ref directly
    assert _caps_ref_for("path", {"caps_ref": "4.M.1"}) == "4.M.1"

    # 2. selection_rules with caps_refs list
    assert _caps_ref_for("path", {"selection_rules": {"caps_refs": ["4.M.2"]}}) == "4.M.2"

    # 3. No caps_ref
    assert _caps_ref_for("path", {}) is None


def test_plan_batch_import_with_statuses_and_locks():
    mock_registry = MagicMock()
    scope1 = MagicMock(scope_id="scope-1", status=MagicMock(value="active"))
    scope2 = MagicMock(scope_id="scope-2", status=MagicMock(value="inactive"))
    mock_registry.list_scopes.return_value = [scope1, scope2]

    mock_review_svc = MagicMock()
    mock_review_status = MagicMock(production_unlocked=True)
    mock_review_svc.review_status.return_value = mock_review_status

    service = ContentFileArtifactImportService(
        registry=mock_registry,
        review_service=mock_review_svc,
    )

    plan1 = FileArtifactImportPlan(
        scope_id="scope-1",
        review_status="approved",
        db_status=ContentArtifactStatus.APPROVED.value,
        records=[],
        errors=[],
        created_count=1,
        updated_count=0,
        validation_report_count=1,
        source_count=1,
    )
    service.plan_scope_import = MagicMock(return_value=plan1)

    batch_plan = service.plan_scope_imports(
        statuses={"active"},
        max_records_per_layer=5,
    )
    assert batch_plan.scope_count == 1
    assert batch_plan.stage_unlocked == 1
    assert batch_plan.production_unlocked == 1
    assert batch_plan.total_records == 0



@pytest.mark.asyncio
async def test_existing_artifact_and_helpers():
    from sqlalchemy.ext.asyncio import AsyncSession
    service = ContentFileArtifactImportService()
    session = MagicMock(spec=AsyncSession)

    record = FileArtifactImportRecord(
        artifact_id=uuid.uuid4(),
        scope_id="scope-1",
        layer="lessons",
        artifact_type="lesson",
        caps_ref="4.M.1",
        artifact_hash="hash-123",
        status="approved",
        source_document_id="doc-1",
        payload_json={"title": "Test"},
    )

    # 1. _existing_artifact: found via session.get
    existing_art = ContentGenerationArtifact(
        artifact_id=record.artifact_id,
        artifact_hash=record.artifact_hash,
    )
    session.get = AsyncMock(return_value=existing_art)
    res1 = await service._existing_artifact(session, record)
    assert res1 == existing_art

    # 2. _existing_artifact: not found via get, found via hash query
    session.get = AsyncMock(return_value=None)
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = existing_art
    session.execute = AsyncMock(return_value=mock_res)

    res2 = await service._existing_artifact(session, record)
    assert res2 == existing_art

    # 3. _has_source without session helper
    mock_src_res = MagicMock()
    mock_src_res.scalar_one_or_none.return_value = MagicMock()
    session.execute = AsyncMock(return_value=mock_src_res)

    assert await service._has_source(session, record) is True

    # 4. _has_validation_report without session helper
    mock_rep_res = MagicMock()
    mock_rep_res.scalar_one_or_none.return_value = MagicMock()
    session.execute = AsyncMock(return_value=mock_rep_res)

    assert await service._has_validation_report(session, record) is True

