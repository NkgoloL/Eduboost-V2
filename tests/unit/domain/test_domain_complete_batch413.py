"""Unit tests for app/domain schemas, models, and domain aggregates - Batch 413.

Targets:
- app/domain/ai_operations_schemas.py
- app/domain/api_v2_models.py
- app/domain/consent.py
- app/domain/content_coverage.py
- app/domain/content_factory_schemas.py
- app/domain/content_review_schemas.py
- app/domain/content_scope.py
- app/domain/content_source.py
- app/domain/curriculum_expansion_schemas.py
- app/domain/data_subject_rights.py
- app/domain/entities.py
- app/domain/irt_quality_schemas.py
- app/domain/item_schema.py
- app/domain/roles.py
- app/domain/schemas.py
- app/domain/trustworthy_beta_quality.py
- app/domain/tutor_schemas.py
"""
import uuid
import datetime
from decimal import Decimal
import pytest
from pydantic import ValidationError

from app.domain.ai_operations_schemas import (
    BudgetCounterView,
    UsageEventView,
    ReservationCancelRequest,
    ReservationView,
)
from app.domain.api_v2_models import (
    ApiMeta,
    FieldError,
    ApiError,
    PaginationMeta,
    ApiEnvelope,
    ApiSuccessEnvelope,
    ApiErrorEnvelope,
    ok,
    fail,
    paginated,
    envelope_content,
    HealthResponse,
    AssessmentAttemptResponseItem,
    AssessmentAttemptRequest,
    StudyPlanGenerateRequest,
    JobAcceptedResponse,
    JobStatusResponse,
    RLHFExportRequest,
)
from app.domain.consent import (
    ConsentState,
    ConsentRecord,
    AuditEventType,
    ALLOWED_TRANSITIONS,
    CONSENT_VALIDITY_DAYS,
)
from app.domain.content_coverage import (
    ContentLayer as CoverageContentLayer,
    CoverageTarget,
    CoverageTargetRegistryDocument,
    CoverageLayerStatus,
    CoverageLayerCounts,
    CapsRefCoverageReport,
    ScopeCoverageSummary,
)
from app.domain.content_factory_schemas import (
    ETLSourceCitation,
    SourceBundleValidationRequest,
    SourceBundleValidationResponse,
    ContentFactoryHealthResponse,
    ContentFactoryETLStatusResponse,
    ContentArtifactCreate,
)
from app.domain.content_review_schemas import (
    ReviewAssignmentCreateRequest,
    ReviewAssignmentAcceptRequest,
    ReviewAssignmentReassignRequest,
    ReviewAssignmentGovernanceResponse,
    ReviewDecisionRequest,
    ReviewDecisionResponse,
    QuarantineRequest,
    ArtifactRevisionRequest,
    ArtifactRevisionResponse,
    ArtifactPublishRequest,
    ArtifactGovernanceStatusResponse,
    ReviewDecisionHistoryItem,
)
from app.domain.content_scope import (
    ContentScopeStatus,
    ContentScope,
    ContentScopeRegistryDocument,
)
from app.domain.content_source import (
    SourceDocumentStatus,
    SourceDocument,
    PlannedSourceRequirements,
    SourceDocumentManifest,
)
from app.domain.curriculum_expansion_schemas import (
    ExpansionPlanRequest,
    CoverageSnapshotRequest,
    TrainingManifestCreateRequest,
    TrainingManifestApproveRequest,
    DatasetExportRequest,
    CoverageSummaryResponse,
)
from app.domain.data_subject_rights import (
    RequestStatus,
    DataExportRequest,
    ErasureRequest,
    CorrectionRequest,
    RestrictionRequest,
)
from app.domain.entities import LearnerProfile, AuditLog
from app.domain.irt_quality_schemas import (
    IRTQualityState,
    IRTInterventionAction,
    IRTQualityPolicy,
    IRTCalibrationObservation,
    IRTCalibrationMetrics,
    IRTCalibrationDecision,
    IRTCalibrationRunRequest,
    IRTCalibrationRunResponse,
    IRTManualOverrideRequest,
)
from app.domain.item_schema import (
    ItemType,
    ReviewStatus,
    ItemSource,
    SubjectCode,
    LanguageCode,
    MCQOption,
    ItemCreate,
    ItemResponse,
)
from app.domain.roles import Role, ROLE_PERMISSIONS, role_has_permission
from app.domain.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse as SchemasTokenResponse,
    RefreshRequest,
    LearnerCreate,
)
from app.domain.trustworthy_beta_quality import (
    TrustworthyBetaQualityRequirement,
    TRUSTWORTHY_BETA_REQUIRED_REQUIREMENTS,
)
from app.domain.tutor_schemas import (
    TutorSessionCreate,
    TutorQuestion,
    TutorMessageView,
    TutorSessionView,
    TutorReply,
    TutorCancelResponse,
)
from app.models.content_factory import ContentArtifactType, ContentLayer, ContentReviewAction


def test_ai_operations_schemas_views():
    now = datetime.datetime.now(datetime.timezone.utc)
    b = BudgetCounterView(
        scope_type="user",
        scope_id="user-123",
        period_key="2026-09",
        used_tokens=100,
        reserved_tokens=50,
        token_limit=1000,
        remaining_tokens=850,
        used_cost_usd=Decimal("0.05"),
        alert_threshold_reached=False,
        updated_at=now,
    )
    assert b.scope_id == "user-123"
    assert b.used_cost_usd == Decimal("0.05")

    ev = UsageEventView(
        event_id=uuid.uuid4(),
        operation_id="op-1",
        user_id="user-1",
        tenant_id="tenant-1",
        purpose="tutor",
        provider="anthropic",
        model="claude-3-haiku",
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30,
        estimated_cost_usd=Decimal("0.001"),
        outcome="success",
        created_at=now,
    )
    assert ev.total_tokens == 30

    cancel = ReservationCancelRequest(reason="Session aborted by user")
    assert cancel.reason == "Session aborted by user"

    res_view = ReservationView(
        reservation_id=uuid.uuid4(),
        operation_id="op-1",
        user_id="user-1",
        tenant_id="tenant-1",
        purpose="tutor",
        estimated_tokens=50,
        status="active",
        failure_reason=None,
        reserved_at=now,
        expires_at=now + datetime.timedelta(minutes=5),
        finalized_at=None,
    )
    assert res_view.status == "active"


def test_api_v2_envelope_and_helpers():
    meta = ApiMeta(request_id="req-999")
    assert meta.api_version == "v2"
    assert meta.request_id == "req-999"

    fe = FieldError(field="username", message="Username is required", code="required")
    err = ApiError(code="VALIDATION_FAILED", message="Validation error", field_errors=[fe], remediation="Provide username", details={"key": "val"})
    assert err.code == "VALIDATION_FAILED"
    assert len(err.field_errors) == 1

    pag = PaginationMeta(limit=20, offset=0, cursor=None, next_cursor="next_1", total=100, has_more=True)
    assert pag.limit == 20
    assert pag.has_more is True

    # ok helper
    resp_ok = ok({"greeting": "hello"}, request_id="req-123")
    assert resp_ok.data == {"greeting": "hello"}
    assert resp_ok.meta.request_id == "req-123"

    # fail helper
    resp_fail = fail(code="NOT_FOUND", message="Item not found", request_id="req-456", field_errors=[fe], remediation="Retry", details={"item": "123"})
    assert resp_fail.error.code == "NOT_FOUND"

    # paginated helper
    resp_pag = paginated(["item1", "item2"], limit=10, request_id="req-789", offset=0, total=2, has_more=False)
    assert resp_pag.data == ["item1", "item2"]
    assert resp_pag.meta.pagination.total == 2

    # envelope_content
    dumped = envelope_content(resp_ok)
    assert dumped["data"] == {"greeting": "hello"}
    assert dumped["meta"]["request_id"] == "req-123"

    # Other models in api_v2_models
    h = HealthResponse(status="ok", version="2.0.0", environment="test", mode="standard")
    assert h.status == "ok"

    att_item = AssessmentAttemptResponseItem(item_id="item-1", selected_option="A", answer="42", metadata={"time": 10})
    att_req = AssessmentAttemptRequest(learner_id="learner-1", responses=[att_item], time_taken_seconds=45)
    assert att_req.time_taken_seconds == 45

    sp_req = StudyPlanGenerateRequest(gap_ratio=0.5)
    assert sp_req.gap_ratio == 0.5

    job_acc = JobAcceptedResponse(job_id="job-1", operation="generate")
    assert job_acc.status == "queued"

    job_stat = JobStatusResponse(
        job_id="job-1",
        operation="generate",
        status="done",
        payload={"task": "lesson"},
        result={"file": "out.json"},
        created_at="2026-09-10T12:00:00Z",
        updated_at="2026-09-10T12:01:00Z",
    )
    assert job_stat.status == "done"

    rlhf = RLHFExportRequest(records=[{"id": 1}])
    assert len(rlhf.records) == 1


def test_consent_record_lifecycle():
    now = datetime.datetime.now(datetime.timezone.utc)
    rec = ConsentRecord(
        learner_id=uuid.uuid4(),
        guardian_id=uuid.uuid4(),
        privacy_notice_version="2026.1",
    )
    assert rec.state == ConsentState.PENDING
    assert rec.is_active() is False
    assert rec.days_until_expiry() is None

    # Grant
    granted = rec.grant("2026.2")
    assert granted.state == ConsentState.GRANTED
    assert granted.is_active() is True
    assert granted.days_until_expiry() == CONSENT_VALIDITY_DAYS
    assert granted.privacy_notice_version == "2026.2"

    # Renew
    renewed = granted.renew("2026.3")
    assert renewed.state == ConsentState.GRANTED
    assert renewed.privacy_notice_version == "2026.3"

    # Mark renewal required
    renewal_req = renewed.mark_renewal_required()
    assert renewal_req.state == ConsentState.RENEWAL_REQUIRED
    assert renewal_req.is_active() is False

    # Withdraw
    withdrawn = renewal_req.withdraw()
    assert withdrawn.state == ConsentState.WITHDRAWN
    assert withdrawn.withdrawn_at is not None

    # Deny from pending
    rec2 = ConsentRecord(
        learner_id=uuid.uuid4(),
        guardian_id=uuid.uuid4(),
        privacy_notice_version="2026.1",
    )
    denied = rec2.deny(reason="Parent opted out")
    assert denied.state == ConsentState.DENIED
    assert denied.denial_reason == "Parent opted out"

    # Regrant from denied
    regranted = denied.grant("2026.2")
    assert regranted.state == ConsentState.GRANTED

    # Mark expired
    expired = regranted.mark_expired()
    assert expired.state == ConsentState.EXPIRED

    # Invalid transition
    with pytest.raises(ValueError, match="Invalid consent transition"):
        rec.mark_expired()

    # is_active past expiry
    past = now - datetime.timedelta(days=10)
    expired_rec = granted.model_copy(update={"expires_at": past})
    assert expired_rec.is_active() is False
    assert expired_rec.days_until_expiry() == 0

    # AuditEventType check
    assert AuditEventType.CONSENT_GRANT == "consent_grant"
    assert AuditEventType.ERASURE_EXECUTION == "erasure_execution"


def test_content_coverage_models():
    target = CoverageTarget(
        scope_id="scope-1",
        caps_ref="CAPS-MATH-G9",
        targets={"lessons": 5, "diagnostic_items": 20},
    )
    assert target.scope_id == "scope-1"

    reg = CoverageTargetRegistryDocument(
        schema_version="1.0",
        targets=[target],
    )
    assert len(reg.targets) == 1

    counts = CoverageLayerCounts(
        target=10,
        approved=8,
        pending_review=2,
        rejected=0,
        generated=10,
        status=CoverageLayerStatus.GREEN,
        coverage_ratio=0.8,
    )
    assert counts.status == CoverageLayerStatus.GREEN

    rep = CapsRefCoverageReport(
        scope_id="scope-1",
        caps_ref="CAPS-MATH-G9",
        layers={CoverageContentLayer.LESSONS: counts},
    )
    assert rep.caps_ref == "CAPS-MATH-G9"

    from app.domain.content_coverage import (
        coverage_status,
        ScopeCoverageSummary,
        ScopeCoverageLayerSummary,
        ScopeCoverageReport,
    )
    assert coverage_status(0, 0) == CoverageLayerStatus.NOT_CONFIGURED
    assert coverage_status(0, 10) == CoverageLayerStatus.RED
    assert coverage_status(5, 10) == CoverageLayerStatus.AMBER
    assert coverage_status(10, 10) == CoverageLayerStatus.GREEN

    sc_sum = ScopeCoverageSummary(
        total_caps_refs=1,
        green_refs=1,
        amber_refs=0,
        red_refs=0,
        not_configured_refs=0,
    )
    layer_sum = ScopeCoverageLayerSummary(target_total=10, approved_total=10, coverage_ratio=1.0)
    report = ScopeCoverageReport(
        scope_id="scope-1",
        grade=9,
        subject_code="MATH",
        language="en",
        summary=sc_sum,
        layers={CoverageContentLayer.LESSONS: layer_sum},
        per_caps_ref=[rep],
    )
    assert report.grade == 9


def test_content_review_schemas_and_validators():
    now = datetime.datetime.now(datetime.timezone.utc)
    req = ReviewAssignmentCreateRequest(
        reviewer_ids=["rev1", "rev2"],
        reviewer_competencies={"rev1": ["math"]},
        priority="high",
        idempotency_key="idemp-key-123",
    )
    assert len(req.reviewer_ids) == 2

    with pytest.raises(ValidationError):
        ReviewAssignmentCreateRequest(reviewer_ids=["rev1", "rev1"])

    accept = ReviewAssignmentAcceptRequest(conflict_of_interest=False)
    assert accept.conflict_of_interest is False

    reassign = ReviewAssignmentReassignRequest(
        new_reviewer_id="rev3",
        reason="Unavailable due to leave",
    )
    assert reassign.new_reviewer_id == "rev3"

    gov_resp = ReviewAssignmentGovernanceResponse(
        assignment_ids=[uuid.uuid4()],
        artifact_id=uuid.uuid4(),
        artifact_version=1,
        assigned_count=1,
    )
    assert gov_resp.assigned_count == 1

    dec_req = ReviewDecisionRequest(
        action=ContentReviewAction.APPROVE,
        expected_version=1,
        idempotency_key="decision-key-123",
    )
    assert dec_req.action == ContentReviewAction.APPROVE

    dec_resp = ReviewDecisionResponse(
        decision_id=uuid.uuid4(),
        artifact_id=uuid.uuid4(),
        artifact_version=1,
        action="approve",
        previous_status="review",
        current_status="approved",
        approval_count=2,
        quorum_threshold=2,
        quorum_reached=True,
    )
    assert dec_resp.quorum_reached is True

    quar = QuarantineRequest(reason_code="SAFETY_FAIL", reason="Contains unacceptable terminology")
    assert quar.reason_code == "SAFETY_FAIL"

    rev_req = ArtifactRevisionRequest(expected_version=1, artifact_json={"content": "revised"}, reason="Fix spelling")
    assert rev_req.expected_version == 1

    rev_resp = ArtifactRevisionResponse(
        previous_artifact_id=uuid.uuid4(),
        new_artifact_id=uuid.uuid4(),
        version_number=2,
        status="review",
    )
    assert rev_resp.version_number == 2

    pub_req = ArtifactPublishRequest(expected_version=2, reason="Approved by dual review")
    assert pub_req.reason == "Approved by dual review"

    gov_stat = ArtifactGovernanceStatusResponse(
        artifact_id=uuid.uuid4(),
        version_number=2,
        status="approved",
        approval_count=2,
        publication_eligible=True,
    )
    assert gov_stat.publication_eligible is True

    hist = ReviewDecisionHistoryItem(
        decision_id=uuid.uuid4(),
        artifact_id=uuid.uuid4(),
        artifact_version=2,
        reviewer_id="rev-1",
        action="approve",
        reason_code=None,
        comments="Clear alignment",
        rubric_id="rubric-v1",
        rubric_version="1.0",
        rubric_results={"math": 1.0},
        policy_version="1.0",
        correlation_id="corr-1",
        created_at=now,
    )
    assert hist.action == "approve"


def test_content_scope_and_source_manifests():
    scope = ContentScope(
        scope_id="scope-caps-9",
        grade=9,
        subject_code="MATH",
        subject="Mathematics",
        language="en",
        curriculum="CAPS",
        status=ContentScopeStatus.ACTIVE,
    )
    assert scope.status == ContentScopeStatus.ACTIVE

    reg_doc = ContentScopeRegistryDocument(schema_version="1.0", scopes=[scope])
    assert len(reg_doc.scopes) == 1

    doc = SourceDocument(
        document_id="doc-dbe-9",
        title="DBE Mathematics Grade 9",
        publisher="DBE",
        curriculum="CAPS",
        phase="Senior Phase",
        grades=[9],
        subjects=["Mathematics"],
        languages=["en"],
        status=SourceDocumentStatus.SOURCE_LOADED,
    )
    assert doc.publisher == "DBE"

    reqs = PlannedSourceRequirements(status="ready", required_fields_before_generation=["title", "publisher"])
    manifest = SourceDocumentManifest(schema_version="1.0", documents=[doc], planned_source_requirements=reqs)
    assert len(manifest.documents) == 1


def test_curriculum_expansion_schemas_strict():
    exp = ExpansionPlanRequest(
        scope_ids=["scope-1", "scope-2"],
        languages=["en", "zu"],
        layers=["lessons"],
        dry_run=False,
    )
    assert len(exp.scope_ids) == 2

    with pytest.raises(ValidationError):
        ExpansionPlanRequest(scope_ids=["scope-1", "scope-1"])

    cov_snap = CoverageSnapshotRequest(scope_ids=["scope-1"], source_commit_sha="abcdef123456")
    assert cov_snap.source_commit_sha == "abcdef123456"

    tr_create = TrainingManifestCreateRequest(
        dataset_version="dataset-v1.0",
        scope_ids=["scope-1"],
        languages=["en"],
    )
    assert tr_create.min_quality_score == 0.80

    tr_app = TrainingManifestApproveRequest(decision="approve", reason="Quality metrics met")
    assert tr_app.decision == "approve"

    export_req = DatasetExportRequest(output_name="export_2026.jsonl")
    assert export_req.output_name == "export_2026.jsonl"

    cov_sum = CoverageSummaryResponse(
        scope_id="scope-1",
        language="en",
        target_total=100,
        approved_total=95,
        gap_count=5,
        status="near_complete",
        details={"audit": "clean"},
    )
    assert cov_sum.gap_count == 5



def test_data_subject_rights_methods():
    now = datetime.datetime.now(datetime.timezone.utc)
    exp = DataExportRequest(learner_id=uuid.uuid4(), requested_by=uuid.uuid4())
    assert exp.is_overdue() is False

    past = now - datetime.timedelta(days=40)
    exp_overdue = exp.model_copy(update={"sla_deadline": past})
    assert exp_overdue.is_overdue() is True

    exp_completed = exp_overdue.model_copy(update={"status": RequestStatus.COMPLETED})
    assert exp_completed.is_overdue() is False

    eras = ErasureRequest(learner_id=uuid.uuid4(), requested_by=uuid.uuid4())
    assert eras.can_execute() is False

    eras_in_prog = eras.model_copy(update={"status": RequestStatus.IN_PROGRESS})
    assert eras_in_prog.can_execute() is True

    eras_held = eras_in_prog.model_copy(update={"legal_hold": True})
    assert eras_held.can_execute() is False

    corr = CorrectionRequest(
        learner_id=uuid.uuid4(),
        requested_by=uuid.uuid4(),
        field_name="home_language",
        old_value="en",
        new_value="zu",
    )
    assert corr.new_value == "zu"

    rest = RestrictionRequest(
        learner_id=uuid.uuid4(),
        requested_by=uuid.uuid4(),
        reason="Disputed identity",
    )
    assert rest.status == RequestStatus.PENDING


def test_entities_dataclasses():
    p = LearnerProfile(learner_id="l-1", grade=9, home_language="zu", overall_mastery=0.85)
    assert p.overall_mastery == 0.85

    log = AuditLog(
        event_id="e-1",
        learner_id="l-1",
        event_type="LESSON_COMPLETED",
        occurred_at=datetime.datetime.now(datetime.timezone.utc),
        payload={"score": 90},
    )
    assert log.event_type == "LESSON_COMPLETED"


def test_irt_quality_schemas_and_validators():
    policy = IRTQualityPolicy()
    assert policy.policy_version == "phase4-v1"

    with pytest.raises(ValidationError):
        # healthy_discrimination_min must be >= monitor_discrimination_min
        IRTQualityPolicy(healthy_discrimination_min=0.4, monitor_discrimination_min=0.5)

    with pytest.raises(ValidationError):
        # quarantine_fit_rmse must be >= max_fit_rmse
        IRTQualityPolicy(quarantine_fit_rmse=0.2, max_fit_rmse=0.35)

    obs = IRTCalibrationObservation(
        learner_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        ability_proxy=0.5,
        is_correct=True,
    )
    assert obs.is_correct is True

    metrics = IRTCalibrationMetrics(
        response_count=150,
        unique_learners=80,
        session_count=30,
        answered_ratio=0.98,
        accuracy=0.75,
        difficulty_b=0.2,
        discrimination_a=1.1,
        guessing_c=0.2,
        fit_rmse=0.25,
        converged=True,
        data_quality_passed=True,
    )
    assert metrics.converged is True

    dec = IRTCalibrationDecision(
        previous_state=IRTQualityState.UNCALIBRATED,
        next_state=IRTQualityState.HEALTHY,
        action=IRTInterventionAction.RETAIN,
        reason="Fitted 2PL parameters within healthy bounds",
        strike_count=0,
    )
    assert dec.action == IRTInterventionAction.RETAIN

    run_req = IRTCalibrationRunRequest(dry_run=True)
    assert run_req.dry_run is True

    run_resp = IRTCalibrationRunResponse(job_id="job-irt-1")
    assert run_resp.status == "queued"

    override = IRTManualOverrideRequest(
        state=IRTQualityState.HEALTHY,
        reason="Manual inspection verified item clarity and correctness",
    )
    assert override.state == IRTQualityState.HEALTHY

    with pytest.raises(ValidationError):
        IRTManualOverrideRequest(
            state=IRTQualityState.UNCALIBRATED,
            reason="Uncalibrated state cannot be manually overridden to",
        )


def test_item_schema_mcq_and_eligibility():
    now = datetime.datetime.now(datetime.timezone.utc)
    opt1 = MCQOption(label="A", text="Option 1")
    opt2 = MCQOption(label="B", text="Option 2")

    item = ItemCreate(
        caps_ref="4.M.1.1",
        grade=4,
        subject=SubjectCode.MATHEMATICS,
        term=1,
        topic="Numbers",
        subtopic="Whole Numbers",
        skill="Addition",
        stem="What is 2 + 2?",
        answer_key="A",
        options=[opt1.model_dump(), opt2.model_dump()],
        explanation="2 + 2 is 4",
        item_type=ItemType.MCQ,
        language=LanguageCode.EN,
    )
    assert item.stem == "What is 2 + 2?"

    # MCQ without options fails validator
    with pytest.raises(ValidationError):
        ItemCreate(
            caps_ref="4.M.1.1",
            grade=4,
            subject=SubjectCode.MATHEMATICS,
            term=1,
            topic="Numbers",
            subtopic="Whole Numbers",
            skill="Addition",
            stem="What is 2 + 2?",
            answer_key="A",
            options=None,
            explanation="2 + 2 is 4",
            item_type=ItemType.MCQ,
        )

    # ItemResponse eligibility property
    item_dict = item.model_dump()
    for field in ["created_at", "review_status", "safety_passed", "exposure_count", "max_exposure"]:
        item_dict.pop(field, None)
    resp = ItemResponse(
        **item_dict,
        created_at=now,
        review_status=ReviewStatus.APPROVED,
        safety_passed=True,
        exposure_count=10,
        max_exposure=50,
    )
    assert resp.is_eligible is True

    resp_exposed = resp.model_copy(update={"exposure_count": 55})
    assert resp_exposed.is_eligible is False

    resp_draft = resp.model_copy(update={"review_status": ReviewStatus.DRAFT})
    assert resp_draft.is_eligible is False


def test_roles_and_permissions():
    assert role_has_permission(Role.ADMIN, "any:permission") is True
    assert role_has_permission(Role.LEARNER, "lesson:read_own") is True
    assert role_has_permission(Role.LEARNER, "billing:manage_own") is False
    assert role_has_permission(Role.GUARDIAN, "learner:read_linked") is True
    assert role_has_permission(Role.COMPLIANCE_AUDITOR, "audit:read") is True


def test_schemas_auth_and_learner():
    reg = RegisterRequest(
        email="user@test.com",
        password="MySpecial#Secret2026",
        display_name="Test User",
        role="parent",
    )
    assert reg.role == "parent"

    login = LoginRequest(email="user@test.com", password="MySpecial#Secret2026")
    assert login.email == "user@test.com"

    tok = SchemasTokenResponse(access_token="tok123", token_type="bearer", expires_in=3600)
    assert tok.expires_in == 3600

    ref = RefreshRequest(refresh_token="ref123")
    assert ref.refresh_token == "ref123"

    learner = LearnerCreate(display_name="Child One", grade=5, language="en")
    assert learner.grade == 5


def test_trustworthy_beta_quality_constants():
    assert len(TRUSTWORTHY_BETA_REQUIRED_REQUIREMENTS) > 0
    req = TRUSTWORTHY_BETA_REQUIRED_REQUIREMENTS[0]
    assert req.required is True
    assert req.key == "feedback_report_issue_button"


def test_tutor_schemas_views():
    now = datetime.datetime.now(datetime.timezone.utc)
    sess_create = TutorSessionCreate(learner_id="learner-1", lesson_id="lesson-1", language="en")
    assert sess_create.language == "en"

    q = TutorQuestion(text="Can you explain this step?", client_message_id="client-msg-1234")
    assert q.client_message_id == "client-msg-1234"

    msg_view = TutorMessageView(
        message_id=uuid.uuid4(),
        role="assistant",
        content="First, factor out the common term.",
        safety_status="passed",
        created_at=now,
    )
    assert msg_view.role == "assistant"

    sess_view = TutorSessionView(
        session_id=uuid.uuid4(),
        learner_id="learner-1",
        lesson_id="lesson-1",
        language="en",
        status="active",
        message_count=1,
        escalation_count=0,
        created_at=now,
        last_activity_at=now,
        messages=[msg_view],
    )
    assert sess_view.message_count == 1

    reply = TutorReply(
        session_id=sess_view.session_id,
        learner_message=msg_view.model_copy(update={"role": "learner"}),
        assistant_message=msg_view,
    )
    assert reply.fallback is False

    cancel = TutorCancelResponse(session_id=sess_view.session_id, status="cancelled")
    assert cancel.status == "cancelled"


def test_learner_and_lesson_domain():
    from app.domain.learner import Learner
    l = Learner(id="l-1", guardian_id="g-1", display_name="Learner", grade=6)
    assert l.grade == 6

    from app.domain.lesson import Lesson, ReviewStatus as LessonReviewStatus, SafetyClassification
    les = Lesson(id="les-1", learner_id="l-1", subject="Math", topic="Fractions", grade=6)
    assert les.topic == "Fractions"
    assert LessonReviewStatus.APPROVED == "approved"
    assert SafetyClassification.SAFE == "safe"


def test_llm_schemas_and_validators():
    from app.domain.llm_schemas import (
        LessonTrustLabel,
        LessonContent,
        StudyPlanContent,
        DiagnosticFeedback,
        DiagnosticItemContract,
    )

    tl = LessonTrustLabel(curriculum_version="2026.1")
    assert tl.ai_generated is True

    lc = LessonContent(
        title="Fractions Introduction",
        introduction="Welcome to fractions",
        main_content="A fraction represents a part of a whole",
        worked_example="1/2 + 1/2 = 1",
        practice_question="What is 1/4 + 1/4?",
        answer="1/2",
        cultural_hook="Sharing a pizza with friends",
        caps_reference="CAPS:2026:MATH-G6",
    )
    assert lc.trust_label.caps_linked is True
    assert lc.trust_label.answer_checked is True
    assert lc.trust_label.safety_checked is True

    with pytest.raises(ValidationError):
        LessonContent(
            title="Bad Caps",
            introduction="Intro",
            main_content="Main",
            worked_example="Ex",
            practice_question="Q",
            answer="A",
            cultural_hook="Hook",
            caps_reference="INVALID-PREFIX",
        )

    sp = StudyPlanContent(week_label="Week 1", daily_topics=["fractions", "decimals"])
    assert len(sp.daily_topics) == 2

    df = DiagnosticFeedback(summary="Good grasp of algebra", encouragement="Keep practicing!", next_steps=["Quadratic equations"])
    assert len(df.next_steps) == 1

    item_contract = DiagnosticItemContract(
        item_id="item-c-1",
        subject="Mathematics",
        grade=8,
        topic="Algebra",
        skill="Solving linear equations",
        difficulty=0.0,
        discrimination=1.0,
        correct_answer="B",
        distractors={"A": "x = 1", "B": "x = 2", "C": "x = 3", "D": "x = 4"},
        explanation="Subtract 2 then divide by 3",
        caps_reference="CAPS:2026:MATH-G8-ALG",
    )
    assert item_contract.correct_answer == "B"

    # Distractors must have exactly A, B, C, D
    with pytest.raises(ValidationError):
        DiagnosticItemContract(
            item_id="item-c-2",
            subject="Mathematics",
            grade=8,
            topic="Algebra",
            skill="Solving linear equations",
            difficulty=0.0,
            discrimination=1.0,
            correct_answer="B",
            distractors={"A": "x = 1", "B": "x = 2"},
            explanation="Subtract 2",
            caps_reference="CAPS:2026:MATH-G8-ALG",
        )


def test_models_compat_import():
    import app.domain.models as domain_models
    assert hasattr(domain_models, "Base") or hasattr(domain_models, "DiagnosticItem")

