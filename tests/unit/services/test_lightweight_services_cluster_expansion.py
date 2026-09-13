import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.consent_expiry_service import (
    consent_expiry_loop,
    run_consent_expiry_scan,
)
from app.services.diagnostic_service_v2 import DiagnosticServiceV2
from app.services.parent_report_service_v2 import ParentReportServiceV2
from app.services.rlhf_service import RLHFService
from app.services.system_service_v2 import SystemServiceV2
from app.services.trustworthy_beta_quality import (
    trustworthy_beta_quality_complete,
    trustworthy_beta_quality_keys,
)


@pytest.mark.asyncio
async def test_parent_report_service_v2_complete():
    learner_repo = AsyncMock()
    report_repo = AsyncMock()
    service = ParentReportServiceV2(learner_repo, report_repo)

    # 1. Learner not found raises ValueError
    learner_repo.get_by_id.return_value = None
    with pytest.raises(ValueError, match="Learner not found"):
        await service.build_report("l1", "g1")

    # 2. Guardian not linked raises PermissionError
    learner_repo.get_by_id.return_value = {"id": "l1"}
    report_repo.verify_guardian_link.return_value = False
    with pytest.raises(PermissionError, match="Guardian is not linked to learner"):
        await service.build_report("l1", "g1")

    with pytest.raises(PermissionError, match="Guardian is not linked to learner"):
        await service.list_reports("l1", "g1")

    # 3. Successful build_report with weak subjects (mastery < 0.5)
    report_repo.verify_guardian_link.return_value = True
    report_repo.get_subject_mastery.return_value = [
        {"subject_code": "MATH", "mastery_score": 0.4},
        {"subject_code": "ENG", "mastery_score": 0.8},
    ]
    report_repo.persist_report.return_value = "rep-1"

    with patch("app.services.parent_report_service_v2.AuditService") as mock_audit_cls:
        mock_audit = AsyncMock()
        mock_audit_cls.return_value = mock_audit
        res = await service.build_report("l1", "g1")
        assert res["report_id"] == "rep-1"
        assert "Priority support needed in MATH." in res["summary"]
        mock_audit.log_event.assert_awaited_once_with("PARENT_REPORT_CREATED", {"report_id": "rep-1"}, "l1")

    # 4. Successful build_report without weak subjects
    report_repo.get_subject_mastery.return_value = [
        {"subject_code": "MATH", "mastery_score": 0.9}
    ]
    with patch("app.services.parent_report_service_v2.AuditService") as mock_audit_cls:
        mock_audit = AsyncMock()
        mock_audit_cls.return_value = mock_audit
        res_steady = await service.build_report("l1", "g1")
        assert res_steady["summary"] == "Learner is progressing steadily."

    # 5. list_reports success
    report_repo.get_reports_for_learner.return_value = [{"id": "rep-1"}]
    assert await service.list_reports("l1", "g1") == [{"id": "rep-1"}]


@pytest.mark.asyncio
async def test_system_service_v2_complete():
    service = SystemServiceV2()
    health = await service.health()
    assert health["status"] == "ok"
    assert "version" in health

    pillars = await service.pillars()
    assert pillars["architecture"] == "modular-monolith"
    assert "diagnostics" in pillars["pillars"]

    schema = await service.schema_status()
    assert schema["status"] == "ok"


@pytest.mark.asyncio
async def test_diagnostic_service_v2_complete():
    learner_repo = AsyncMock()
    quota_svc = AsyncMock()
    diag_repo = AsyncMock()
    service = DiagnosticServiceV2(learner_repo, quota_svc, diag_repo)

    # 1. Learner not found
    learner_repo.get_by_id.return_value = None
    with pytest.raises(ValueError, match="Learner not found"):
        await service.run_diagnostic("l1", "MATH")

    # 2. Cached response available
    learner_repo.get_by_id.return_value = {"id": "l1"}
    quota_svc.get_cached.return_value = {"session_id": "cached-1"}
    cached_res = await service.run_diagnostic("l1", "MATH")
    assert cached_res["session_id"] == "cached-1"

    # 3. Cache miss: session created
    quota_svc.get_cached.return_value = None
    diag_repo.create_session.return_value = type("Session", (), {"session_id": "sess-new"})()
    new_res = await service.run_diagnostic("l1", "MATH")
    assert new_res["session_id"] == "sess-new"
    assert new_res["subject_code"] == "MATH"


def test_rlhf_service_complete():
    service = RLHFService()
    records = [{"input": "2 + 2", "output": "4"}]

    openai_res = service.export_openai_format(records)
    assert openai_res["format"] == "openai"
    assert openai_res["record_count"] == 1

    anthropic_res = service.export_anthropic_format(records)
    assert anthropic_res["format"] == "anthropic"
    assert anthropic_res["record_count"] == 1


def test_trustworthy_beta_quality_complete():
    keys = trustworthy_beta_quality_keys()
    assert isinstance(keys, list)
    assert len(keys) > 0

    assert trustworthy_beta_quality_complete(set(keys)) is True
    assert trustworthy_beta_quality_complete(set()) is False


@pytest.mark.asyncio
async def test_consent_expiry_service_complete():
    # 1. run_consent_expiry_scan
    with patch("app.services.consent_expiry_service.AsyncSessionLocal") as mock_sess_cls, \
         patch("app.services.consent_expiry_service.ConsentRenewalService") as mock_renewal_cls:
        mock_sess = AsyncMock()
        mock_sess_cls.return_value.__aenter__.return_value = mock_sess
        mock_renewal = AsyncMock()
        mock_renewal.run.return_value = {"reminded": 5}
        mock_renewal_cls.return_value = mock_renewal

        reminded = await run_consent_expiry_scan()
        assert reminded == 5

    # 2. consent_expiry_loop single iteration with success and sleep break
    call_count = 0
    async def mock_run_once():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return 3
        raise RuntimeError("simulated error")

    sleep_count = 0
    async def mock_sleep(interval):
        nonlocal sleep_count
        sleep_count += 1
        if sleep_count >= 2:
            raise asyncio.CancelledError()

    with patch("asyncio.sleep", mock_sleep):
        with pytest.raises(asyncio.CancelledError):
            await consent_expiry_loop(interval_seconds=1, run_once=mock_run_once)

    assert call_count == 2
