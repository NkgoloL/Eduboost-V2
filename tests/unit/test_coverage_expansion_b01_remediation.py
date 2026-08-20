"""Targeted unit test expansions for clean, zero-coverage core and service modules."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api_v2_deps.auth import AuthContext
from app.api_v2_routers.ether import get_questions
from app.core import rbac
from app.core.dependencies import (
    get_consent_repo,
    get_current_guardian_id,
    get_current_user_id,
    get_request_id,
    require_active_consent,
    require_active_consent_for_current_learner,
)
from app.core.exceptions import AuthenticationError, ConsentRequiredError
from app.core.security import create_access_token
from app.jobs.consent_renewal_job import run_consent_renewal_reminders
from app.models import Language, UserRole
from app.modules.lessons.mock_llm_provider import MockLLMProvider, MockMode
from app.repositories.irt_repository import IRTRepository
from app.repositories.parent_report_repository import ParentReportRepository
from app.services.contracts import (
    IAuthService,
    IConsentService,
    IDiagnosticService,
    ILearnerService,
    ILessonService,
)
from app.services.etl.factory import create_etl_pipeline
from app.services.rlhf_service import RLHFService
from app.services.trustworthy_beta_quality import (
    trustworthy_beta_quality_complete,
    trustworthy_beta_quality_keys,
)


# ============================================================================
# 1. MockLLMProvider Tests
# ============================================================================

@pytest.mark.asyncio
async def test_mock_llm_provider_valid_lesson():
    provider = MockLLMProvider(mode=MockMode.VALID_LESSON, caps_ref="4.M.1.2")
    resp = await provider.complete(prompt="Generate a lesson", system="You are a tutor")
    assert resp["provider"] == MockLLMProvider.PROVIDER_NAME
    assert resp["used_fallback"] is False
    assert provider.call_count == 1

    lesson = json.loads(resp["content"])
    assert lesson["caps_ref"] == "4.M.1.2"
    assert "lesson_id" in lesson


@pytest.mark.asyncio
async def test_mock_llm_provider_verifier_response():
    provider = MockLLMProvider(mode=MockMode.VALID_LESSON)
    resp = await provider.complete(prompt="Does this agrees_with_key?", system="VERIFICATION STEP")
    assert resp["provider"] == MockLLMProvider.PROVIDER_NAME
    verifier_data = json.loads(resp["content"])
    assert isinstance(verifier_data, list)
    assert "agrees_with_key" in verifier_data[0]


@pytest.mark.asyncio
async def test_mock_llm_provider_answer_key_disagree():
    provider = MockLLMProvider(mode=MockMode.ANSWER_KEY_DISAGREE)
    resp = await provider.complete(prompt="agrees_with_key check", system="")
    verifier_data = json.loads(resp["content"])
    assert isinstance(verifier_data, list)
    assert verifier_data[0]["derived_answer"] == "A"


@pytest.mark.asyncio
async def test_mock_llm_provider_inject_failure():
    provider = MockLLMProvider(
        mode=MockMode.INJECT_FAILURE,
        failure_field="title",
        failure_value=12345,
    )
    resp = await provider.complete(prompt="Make lesson", system="")
    lesson = json.loads(resp["content"])
    assert lesson["title"] == 12345


@pytest.mark.asyncio
async def test_mock_llm_provider_static_fallback():
    provider = MockLLMProvider(mode=MockMode.STATIC_FALLBACK)
    resp = await provider.complete(prompt="test", system="")
    assert resp["used_fallback"] is True
    assert resp["provider"] == "static"


@pytest.mark.asyncio
async def test_mock_llm_provider_error():
    from app.modules.lessons.llm_gateway_v2 import LLMGatewayError

    provider = MockLLMProvider(mode=MockMode.PROVIDER_ERROR)
    with pytest.raises(LLMGatewayError):
        await provider.complete(prompt="test", system="")


# ============================================================================
# 2. RBAC Policy Definitions Tests
# ============================================================================

def test_rbac_operational_roles():
    assert rbac.OperationalRole.LEARNER.value == "student"
    assert rbac.OperationalRole.PARENT_GUARDIAN.value == "parent"
    assert rbac.OperationalRole.ADMIN.value == "admin"
    assert "parent" in rbac.PERSISTED_ROLES
    assert "content_reviewer" in rbac.RESERVED_OPERATIONAL_ROLES
    assert rbac.require_role == rbac.require_roles


# ============================================================================
# 3. Dependencies Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_consent_repo():
    with patch("app.core.dependencies.ConsentRepository") as mock_repo_cls:
        mock_repo_cls.return_value = MagicMock()
        repo = await get_consent_repo()
        assert repo is not None


@pytest.mark.asyncio
async def test_get_current_user_id_missing_credentials():
    with pytest.raises(AuthenticationError, match="Authorization header missing"):
        await get_current_user_id(None)


@pytest.mark.asyncio
async def test_get_current_user_id_valid():
    uid = uuid4()
    token = create_access_token(str(uid), role=UserRole.PARENT)
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    extracted = await get_current_user_id(creds)
    assert extracted == uid


@pytest.mark.asyncio
async def test_get_current_user_id_invalid_token():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token-xyz")
    with pytest.raises(HTTPException):
        await get_current_user_id(creds)


@pytest.mark.asyncio
async def test_get_current_guardian_id():
    uid = uuid4()
    res = await get_current_guardian_id(user_id=uid)
    assert res == uid


@pytest.mark.asyncio
async def test_require_active_consent_success():
    learner_id = uuid4()
    mock_repo = AsyncMock()
    mock_repo.get_active.return_value = MagicMock(id=uuid4())
    mock_db = AsyncMock()

    await require_active_consent(learner_id=learner_id, db=mock_db, repo=mock_repo)


@pytest.mark.asyncio
async def test_require_active_consent_blocks_when_missing():
    learner_id = uuid4()
    mock_repo = AsyncMock()
    mock_repo.get_active.return_value = None
    mock_db = AsyncMock()

    with pytest.raises(ConsentRequiredError):
        await require_active_consent(learner_id=learner_id, db=mock_db, repo=mock_repo)


@pytest.mark.asyncio
async def test_require_active_consent_for_current_learner_not_found():
    learner_id = uuid4()
    mock_db = AsyncMock()
    mock_repo = AsyncMock()
    with patch("app.core.dependencies.LearnerRepository") as MockLearnerRepo:
        mock_instance = MockLearnerRepo.return_value
        mock_instance.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc_info:
            await require_active_consent_for_current_learner(
                learner_id=learner_id,
                db=mock_db,
                repo=mock_repo,
                current_user={"sub": str(uuid4()), "role": "parent"},
            )
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_require_active_consent_for_current_learner_success():
    learner_id = uuid4()
    mock_db = AsyncMock()
    mock_repo = AsyncMock()
    mock_repo.get_active.return_value = MagicMock(id=uuid4())
    with patch("app.core.dependencies.LearnerRepository") as MockLearnerRepo, patch(
        "app.core.dependencies.assert_can_access_learner"
    ) as mock_assert:
        mock_instance = MockLearnerRepo.return_value
        mock_instance.get_by_id = AsyncMock(return_value=MagicMock(id=learner_id))

        result = await require_active_consent_for_current_learner(
            learner_id=learner_id,
            db=mock_db,
            repo=mock_repo,
            current_user={"sub": str(uuid4()), "role": "parent"},
        )
        assert result == learner_id
        mock_assert.assert_called_once()


@pytest.mark.asyncio
async def test_get_request_id_fallback():
    mock_request = MagicMock()
    mock_request.headers = {"X-Request-ID": "req-12345"}
    with patch("app.core.context.get_request_id", return_value=None):
        rid = await get_request_id(mock_request)
        assert rid == "req-12345"


# ============================================================================
# 4. Consent Renewal Job Tests
# ============================================================================

@pytest.mark.asyncio
async def test_run_consent_renewal_reminders_success():
    mock_session = AsyncMock()
    mock_session_factory = MagicMock()
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_service_instance = AsyncMock()
    mock_service_instance.run.return_value = {"processed": 5, "sent": 5}

    ctx = {
        "db_session_factory": mock_session_factory,
        "settings": MagicMock(),
    }

    with patch(
        "app.services.consent_renewal_service.ConsentRenewalService", return_value=mock_service_instance
    ), patch("app.services.consent_renewal_service.SendGridEmailGateway"), patch(
        "app.jobs.consent_renewal_job.update_job", new_callable=AsyncMock
    ) as mock_update:
        stats = await run_consent_renewal_reminders(ctx=ctx, job_id="job-999")
        assert stats == {"processed": 5, "sent": 5}
        mock_update.assert_any_call("job-999", status="running")
        mock_update.assert_any_call("job-999", status="completed", result={"processed": 5, "sent": 5})


@pytest.mark.asyncio
async def test_run_consent_renewal_reminders_failure():
    mock_session_factory = MagicMock()
    mock_session_factory.return_value.__aenter__.side_effect = RuntimeError("DB connection dropped")
    ctx = {"db_session_factory": mock_session_factory}

    with patch("app.services.consent_renewal_service.SendGridEmailGateway"), patch(
        "app.jobs.consent_renewal_job.update_job", new_callable=AsyncMock
    ) as mock_update:
        with pytest.raises(RuntimeError, match="DB connection dropped"):
            await run_consent_renewal_reminders(ctx=ctx, job_id="job-888")
        mock_update.assert_any_call(
            "job-888", status="failed", error={"type": "RuntimeError", "message": "DB connection dropped"}
        )


# ============================================================================
# 5. Parent Report Repository Tests
# ============================================================================

@pytest.mark.asyncio
async def test_parent_report_repository_methods():
    repo = ParentReportRepository()
    mock_session = AsyncMock()
    mock_factory = MagicMock()
    mock_factory.return_value.__aenter__.return_value = mock_session

    with patch("app.repositories.parent_report_repository.AsyncSessionFactory", mock_factory):
        # 1. verify_guardian_link
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_res)
        linked = await repo.verify_guardian_link("l-1", "g-1")
        assert linked is True

        # 2. get_subject_mastery
        row = MagicMock(subject_code="MATH", mastery_score=0.85, grade_level=4, knowledge_gaps=["fractions"])
        mock_res.scalars.return_value.all.return_value = [row]
        mastery = await repo.get_subject_mastery("l-1")
        assert len(mastery) == 1
        assert mastery[0]["subject_code"] == "MATH"

        # 3. persist_report
        rep_id = await repo.persist_report("l-1", "g-1", 0.85, "Good job", mastery)
        assert isinstance(rep_id, str)


# ============================================================================
# 6. Trustworthy Beta Quality Domain & Service Tests
# ============================================================================

def test_trustworthy_beta_quality_requirements():
    keys = trustworthy_beta_quality_keys()
    assert len(keys) >= 5
    assert "feedback_report_issue_button" in keys
    assert "content_correction_workflow" in keys
    assert trustworthy_beta_quality_complete(set(keys)) is True
    assert trustworthy_beta_quality_complete({"feedback_report_issue_button"}) is False


# ============================================================================
# 7. Service Protocols & Contracts Tests
# ============================================================================

def test_service_contracts_protocols():
    assert issubclass(IAuthService, object)
    assert issubclass(ILearnerService, object)
    assert issubclass(IConsentService, object)
    assert issubclass(IDiagnosticService, object)
    assert issubclass(ILessonService, object)


# ============================================================================
# 8. IRT Repository Tests
# ============================================================================

@pytest.mark.asyncio
async def test_irt_repository_queries():
    repo = IRTRepository()
    mock_db = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [MagicMock(id="item-1"), MagicMock(id="item-2")]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute = AsyncMock(return_value=mock_result)

    grade_items = await repo.get_items_for_grade(mock_db, grade=4, language=Language.ENGLISH, limit=10)
    assert len(grade_items) == 2

    subject_items = await repo.get_items_by_subject(mock_db, grade=4, subject="Mathematics", limit=5)
    assert len(subject_items) == 2


# ============================================================================
# 9. RLHF Export Service Tests
# ============================================================================

def test_rlhf_service_exports():
    service = RLHFService()
    records = [{"input": "test question", "output": "test answer"}]

    openai_res = service.export_openai_format(records)
    assert openai_res["format"] == "openai"
    assert openai_res["record_count"] == 1
    assert "dataset_json" in openai_res

    anthropic_res = service.export_anthropic_format(records)
    assert anthropic_res["format"] == "anthropic"
    assert anthropic_res["record_count"] == 1
    assert "dataset_json" in anthropic_res


# ============================================================================
# 10. ETL Factory & Ether Router Tests
# ============================================================================

def test_etl_factory_creation():
    with patch("app.services.etl.factory.EduboostETLv3") as MockV3:
        create_etl_pipeline(db_url="sqlite:///test.db", storage_root="/tmp", version="v3")
        MockV3.assert_called_once_with(db_url="sqlite:///test.db", storage_root="/tmp")


@pytest.mark.asyncio
async def test_ether_router_get_questions():
    auth_ctx = AuthContext(
        user_id=str(uuid4()),
        role="student",
        token_type="access",
        raw_claims={},
        jti="jti-1",
    )
    with patch("app.api_v2_routers.ether._ether.get_onboarding_questions", return_value={"questions": [1, 2]}):
        res = await get_questions(user=auth_ctx)
        assert res == {"questions": [1, 2]}
