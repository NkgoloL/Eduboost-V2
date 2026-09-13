"""Unit tests for production readiness contracts - Batch 414.

Targets:
- app/modules/final_release_blockers/production_readiness_contracts.py (from 0% -> 100%)
- app/modules/roadmap/production_readiness_contracts.py (from 0% -> 100%)
- app/modules/billing/production_readiness_contracts.py (from 67.3% -> >95%)
- app/modules/diagnostics/production_readiness_contracts.py (from 83.3% -> >95%)
"""
from datetime import date, datetime, timezone
import pytest

from app.modules.final_release_blockers.production_readiness_contracts import (
    ReleaseBlockerDomain,
    BlockerSeverity,
    BlockerStatus,
    LaunchAuthority,
    FinalDecision,
    FinalReleaseBlockerDecision,
    ReleaseBlockerItem,
    ReleaseBlockerDomainSummary,
    ReleaseWaiverRule,
    ExternalManualDependency,
    FinalGoNoGoChecklist,
    ReleaseBlockerClosureRecord,
    compute_release_blocker_checksum,
    summarize_blockers,
    determine_final_decision,
    validate_final_release_bundle,
    default_final_release_blocker_readiness_report,
    DEFAULT_FINAL_BLOCKER_DECISION,
    DEFAULT_DOMAIN_SUMMARIES,
    DEFAULT_RELEASE_BLOCKERS,
    DEFAULT_WAIVER_RULES,
    DEFAULT_EXTERNAL_DEPENDENCIES,
    DEFAULT_FINAL_CHECKLIST,
    DEFAULT_CLOSURE_RECORDS,
)
from app.modules.roadmap.production_readiness_contracts import (
    RoadmapHorizon,
    RoadmapCategory,
    RoadmapStatus,
    BaselineBoundary,
    DependencyType,
    PriorityLevel,
    RoadmapGovernanceDecision,
    BaselineBoundaryItem,
    RoadmapItem,
    DeferredScopeItem,
    RoadmapDependency,
    GraduationCriterion,
    RoadmapReviewCadence,
    PostBaselineRisk,
    compute_roadmap_checksum,
    summarize_roadmap_horizons,
    validate_roadmap_bundle,
    default_post_baseline_roadmap_readiness_report,
    DEFAULT_ROADMAP_DECISION,
    DEFAULT_BASELINE_BOUNDARIES,
    DEFAULT_ROADMAP_ITEMS,
    DEFAULT_DEFERRED_SCOPE,
    DEFAULT_DEPENDENCIES,
    DEFAULT_GRADUATION_CRITERIA,
    DEFAULT_REVIEW_CADENCE,
    DEFAULT_POST_BASELINE_RISKS,
)
from app.modules.billing.production_readiness_contracts import (
    BillingProvider,
    SubscriptionState,
    BillingPlan,
    BillingProviderDecision,
    PricingPolicy,
    ALLOWED_TRANSITIONS,
    validate_subscription_transition,
    SubscriptionSnapshot,
    compute_webhook_signature,
    verify_webhook_signature,
    WebhookIdempotencyStore,
    WebhookRetryPolicy,
    BillingAuditEvent,
    default_billing_readiness_report,
)

from app.modules.diagnostics.production_readiness_contracts import (
    DiagnosticItemSpec,
    ItemReviewStatus,
    BiasDimension,
    validate_diagnostic_item_schema,
    irt_probability,
    fisher_information,
    select_item_by_fisher_information,
    grade_equivalent_from_theta,
    identify_gap_topics,
    can_transition_review_status,
    audit_minimum_viable_item_bank,
    required_bias_review_dimensions,
    remediation_tags_from_misconceptions,
)




def test_final_release_blockers_readiness_report_and_defaults():
    rep = default_final_release_blocker_readiness_report()
    assert rep["computed_decision"] == FinalDecision.GO.value
    assert isinstance(rep["checksum_sample"], str)
    assert len(rep["final_bundle_issues"]) == 0

    # Decision validation failure branches
    bad_dec = FinalReleaseBlockerDecision(
        adr_path="invalid/path.md",
        architecture_doc_path="invalid/path.md",
        blocker_checklist_required=False,
        owner_assignment_required=False,
        closure_evidence_required=False,
        waiver_policy_required=False,
        external_dependency_boundary_required=False,
        launch_authority_required=False,
        final_go_no_go_required=False,
    )
    issues = bad_dec.validate()
    assert len(issues) >= 8

    # BlockerItem validation branches
    bad_item = ReleaseBlockerItem(
        blocker_id="INVALID",
        domain=ReleaseBlockerDomain.REPOSITORY,
        title="",
        severity=BlockerSeverity.RELEASE_BLOCKER,
        status=BlockerStatus.WAIVED,
        owner="",
        evidence_path="uncontrolled/path",
        closure_path="uncontrolled/closure",
        waiver_path="uncontrolled/waiver",
        external_dependency=None,
        blocks_launch=True,
    )
    b_issues = bad_item.validate()
    assert any("RB-###" in i for i in b_issues)
    assert any("title is required" in i for i in b_issues)
    assert any("owner is required" in i for i in b_issues)
    assert any("severity cannot be waived" in i for i in b_issues)

    # Closed blocker without closure path
    closed_no_path = ReleaseBlockerItem(
        blocker_id="RB-100",
        domain=ReleaseBlockerDomain.REPOSITORY,
        title="Test",
        severity=BlockerSeverity.LOW,
        status=BlockerStatus.CLOSED,
        owner="owner",
        evidence_path="docs/test.md",
        closure_path=None,
        waiver_path=None,
        external_dependency=None,
        blocks_launch=False,
    )
    assert any("closed blockers require closure evidence" in i for i in closed_no_path.validate())

    # Waived blocker without waiver path
    waived_no_path = ReleaseBlockerItem(
        blocker_id="RB-101",
        domain=ReleaseBlockerDomain.REPOSITORY,
        title="Test",
        severity=BlockerSeverity.LOW,
        status=BlockerStatus.WAIVED,
        owner="owner",
        evidence_path="docs/test.md",
        closure_path=None,
        waiver_path=None,
        external_dependency=None,
        blocks_launch=False,
    )
    assert any("waived blockers require waiver evidence" in i for i in waived_no_path.validate())

    # External pending without note
    ext_no_note = ReleaseBlockerItem(
        blocker_id="RB-102",
        domain=ReleaseBlockerDomain.EXTERNAL_MANUAL,
        title="Test",
        severity=BlockerSeverity.LOW,
        status=BlockerStatus.EXTERNAL_PENDING,
        owner="owner",
        evidence_path="docs/test.md",
        closure_path=None,
        waiver_path=None,
        external_dependency=None,
        blocks_launch=False,
    )
    assert any("external pending blockers require external dependency note" in i for i in ext_no_note.validate())

    # Critical open
    crit_open = ReleaseBlockerItem(
        blocker_id="RB-103",
        domain=ReleaseBlockerDomain.SECURITY,
        title="Test",
        severity=BlockerSeverity.CRITICAL,
        status=BlockerStatus.OPEN,
        owner="owner",
        evidence_path="docs/test.md",
        closure_path=None,
        waiver_path=None,
        external_dependency=None,
        blocks_launch=True,
    )
    assert any("critical/release-blocker items cannot remain open" in i for i in crit_open.validate())

    # Domain summary failure branches
    bad_summary = ReleaseBlockerDomainSummary(
        domain=ReleaseBlockerDomain.REPOSITORY,
        checklist_path="invalid/path.md",
        check_command="",
        owner="",
        required_for_release=True,
        evidence_complete=False,
    )
    s_issues = bad_summary.validate()
    assert any("domain checklist path must live under docs/" in i for i in s_issues)
    assert any("domain check command is required" in i for i in s_issues)
    assert any("domain summary owner is required" in i for i in s_issues)
    assert any("release evidence is incomplete" in i for i in s_issues)


    # Waiver rule validation branches
    bad_waiver = ReleaseWaiverRule(
        rule_id="",
        severity=BlockerSeverity.RELEASE_BLOCKER,
        waiver_allowed=True,
        required_approvers=(),
        expiry_days=0,
        compensating_controls_required=False,
        evidence_path="invalid/path.md",
    )
    w_issues = bad_waiver.validate()
    assert any("rule_id is required" in i for i in w_issues)
    assert any("release-blocker severity cannot be waived" in i for i in w_issues)
    assert any("waiver requires approvers" in i for i in w_issues)
    assert any("expiry must be between 1 and 30 days" in i for i in w_issues)
    assert any("requires compensating controls" in i for i in w_issues)
    assert any("evidence path must live under docs/release_blockers/" in i for i in w_issues)

    # ExternalManualDependency branches
    bad_ext = ExternalManualDependency(
        dependency_id="INVALID",
        description="",
        owner="",
        external_system="",
        verification_method="",
        required_before_launch=True,
        evidence_path="invalid/path.md",
        status=BlockerStatus.OPEN,
    )
    e_issues = bad_ext.validate()
    assert any("EXT-###" in i for i in e_issues)
    assert any("description is required" in i for i in e_issues)
    assert any("owner is required" in i for i in e_issues)
    assert any("external system is required" in i for i in e_issues)
    assert any("verification method is required" in i for i in e_issues)
    assert any("evidence path must live under docs/release_blockers/" in i for i in e_issues)
    assert any("required external dependency is not closed" in i for i in e_issues)

    # FinalGoNoGoChecklist branches
    bad_chk = FinalGoNoGoChecklist(
        checklist_id="",
        decision=FinalDecision.GO,
        approvers=(),
        required_domains=(),
        blocker_register_path="invalid/path.md",
        evidence_bundle_path="invalid/path.md",
        known_issues_reviewed=False,
        rollback_reviewed=False,
        support_reviewed=False,
        privacy_security_reviewed=False,
        external_dependencies_reviewed=False,
    )
    chk_issues = bad_chk.validate()
    assert any("checklist_id is required" in i for i in chk_issues)
    assert any("approvers are required" in i for i in chk_issues)
    assert any("required domains are required" in i for i in chk_issues)

    # ReleaseBlockerClosureRecord branches
    bad_close = ReleaseBlockerClosureRecord(
        closure_id="INVALID",
        blocker_id="INVALID",
        closed_on=date(2026, 1, 1),
        closed_by="",
        evidence_checksum="short",
        evidence_path="invalid/path.md",
        residual_risk="",
        follow_up_required=False,
    )
    cl_issues = bad_close.validate()
    assert any("CLOSE-###" in i for i in cl_issues)
    assert any("RB-###" in i for i in cl_issues)
    assert any("closed_by is required" in i for i in cl_issues)
    assert any("64 lowercase hex" in i for i in cl_issues)
    assert any("closure evidence path must be controlled" in i for i in cl_issues)
    assert any("residual risk summary is required" in i for i in cl_issues)

    # determine_final_decision variations
    open_blocker = ReleaseBlockerItem("RB-099", ReleaseBlockerDomain.SECURITY, "Open Blocker", BlockerSeverity.HIGH, BlockerStatus.OPEN, "owner", "docs/test.md", None, None, None, True)
    assert determine_final_decision((open_blocker,), ()) == FinalDecision.NO_GO

    ext_blocking = ExternalManualDependency("EXT-099", "Blocking Ext", "owner", "sys", "method", True, "docs/release_blockers/ext.md", BlockerStatus.OPEN)
    assert determine_final_decision((), (ext_blocking,)) == FinalDecision.DEFER

    waived_blocker = ReleaseBlockerItem("RB-098", ReleaseBlockerDomain.SECURITY, "Waived Blocker", BlockerSeverity.LOW, BlockerStatus.WAIVED, "owner", "docs/test.md", None, "docs/release_blockers/waiver.md", None, False)
    assert determine_final_decision((waived_blocker,), ()) == FinalDecision.CONDITIONAL_GO




def test_roadmap_readiness_report_and_defaults():
    rep = default_post_baseline_roadmap_readiness_report()
    assert isinstance(rep["checksum_sample"], str)
    assert len(rep["roadmap_bundle_issues"]) == 0
    assert rep["horizon_summary"][RoadmapHorizon.NEXT.value] >= 1

    # RoadmapGovernanceDecision branches
    bad_dec = RoadmapGovernanceDecision(
        adr_path="invalid/path.md",
        architecture_doc_path="invalid/path.md",
        roadmap_owner_required=False,
        deferred_scope_register_required=False,
        dependency_mapping_required=False,
        prioritization_required=False,
        graduation_criteria_required=False,
        baseline_boundary_required=False,
        review_cadence_required=False,
    )
    d_issues = bad_dec.validate()
    assert len(d_issues) >= 8

    # BaselineBoundaryItem branches
    bad_bound = BaselineBoundaryItem(
        boundary_id="",
        area=RoadmapCategory.ENGINEERING,
        title="",
        boundary=BaselineBoundary.EXTERNAL_MANUAL,
        rationale="",
        evidence_path="invalid/path.md",
        owner="",
        manual_dependency=None,
    )
    b_issues = bad_bound.validate()
    assert any("boundary_id is required" in i for i in b_issues)
    assert any("baseline boundary title is required" in i for i in b_issues)
    assert any("baseline boundary rationale is required" in i for i in b_issues)
    assert any("baseline boundary evidence path must be controlled" in i for i in b_issues)
    assert any("baseline boundary owner is required" in i for i in b_issues)
    assert any("external/manual boundary requires manual dependency" in i for i in b_issues)

    # RoadmapItem branches
    bad_item = RoadmapItem(
        roadmap_id="INVALID",
        title="",
        category=RoadmapCategory.PRODUCT,
        horizon=RoadmapHorizon.PARKED,
        status=RoadmapStatus.IN_PROGRESS,
        priority=PriorityLevel.P0,
        owner="",
        rationale="",
        expected_outcome="",
        evidence_path="invalid/path.md",
        target_quarter=None,
    )
    rm_issues = bad_item.validate()
    assert any("RM-###" in i for i in rm_issues)
    assert any("roadmap item title is required" in i for i in rm_issues)
    assert any("P0/P1 items cannot be parked" in i for i in rm_issues)
    assert any("in-progress items must be now or next" in i for i in rm_issues)
    assert any("evidence path must live under docs/roadmap/" in i for i in rm_issues)

    # DeferredScopeItem branches
    bad_def = DeferredScopeItem(
        deferred_id="INVALID",
        title="",
        category=RoadmapCategory.COMMERCIAL,
        reason_deferred="",
        unblock_condition="",
        owner="",
        risk_if_deferred="",
        evidence_path="invalid/path.md",
        review_date=date(2025, 1, 1),
    )
    def_issues = bad_def.validate(date(2026, 1, 1))
    assert any("DEF-###" in i for i in def_issues)
    assert any("deferred title is required" in i for i in def_issues)
    assert any("deferred reason is required" in i for i in def_issues)
    assert any("unblock condition is required" in i for i in def_issues)
    assert any("deferred scope owner is required" in i for i in def_issues)
    assert any("risk if deferred is required" in i for i in def_issues)
    assert any("deferred scope evidence path must live under docs/roadmap/" in i for i in def_issues)
    assert any("deferred scope review date is stale" in i for i in def_issues)

    # RoadmapDependency branches
    bad_dep = RoadmapDependency(
        dependency_id="INVALID",
        source_roadmap_id="INVALID",
        dependency_type=DependencyType.COMMERCIAL,
        description="",
        owner="",
        external=True,
        mitigation="",
        evidence_path="invalid/path.md",
    )
    dep_issues = bad_dep.validate()
    assert any("DEP-###" in i for i in dep_issues)
    assert any("RM-###" in i for i in dep_issues)
    assert any("dependency description is required" in i for i in dep_issues)
    assert any("dependency owner is required" in i for i in dep_issues)
    assert any("external dependencies require mitigation" in i for i in dep_issues)
    assert any("evidence path must live under docs/roadmap/" in i for i in dep_issues)

    # GraduationCriterion branches
    bad_grad = GraduationCriterion(
        criterion_id="INVALID",
        roadmap_id="INVALID",
        metric_name="",
        threshold="",
        evidence_path="invalid/path.md",
        owner="",
        required_for_ga=True,
    )
    grad_issues = bad_grad.validate()
    assert any("GRAD-###" in i for i in grad_issues)
    assert any("RM-###" in i for i in grad_issues)
    assert any("graduation metric name is required" in i for i in grad_issues)
    assert any("graduation threshold is required" in i for i in grad_issues)
    assert any("graduation evidence path must be controlled" in i for i in grad_issues)
    assert any("graduation criterion owner is required" in i for i in grad_issues)

    # RoadmapReviewCadence branches
    bad_cadence = RoadmapReviewCadence(
        cadence_id="",
        frequency_days=0,
        owner="",
        required_inputs=(),
        required_outputs=(),
        evidence_path="invalid/path.md",
        blocks_scope_expansion=False,
    )
    cad_issues = bad_cadence.validate()
    assert any("cadence_id is required" in i for i in cad_issues)
    assert any("frequency must be positive" in i for i in cad_issues)
    assert any("roadmap review requires inputs" in i for i in cad_issues)
    assert any("roadmap review requires outputs" in i for i in cad_issues)
    assert any("evidence path must live under docs/roadmap/" in i for i in cad_issues)
    assert any("roadmap review must block uncontrolled scope expansion" in i for i in cad_issues)


    # PostBaselineRisk branches
    bad_risk = PostBaselineRisk(
        risk_id="INVALID",
        title="",
        category=RoadmapCategory.OPERATIONS,
        impact="critical",
        likelihood="extreme",
        owner="",
        mitigation="",
        evidence_path="invalid/path.md",
        blocks_ga=False,
    )
    risk_issues = bad_risk.validate()
    assert any("RISK-###" in i for i in risk_issues)
    assert any("risk title is required" in i for i in risk_issues)
    assert any("risk likelihood is invalid" in i for i in risk_issues)
    assert any("risk owner is required" in i for i in risk_issues)
    assert any("risk mitigation is required" in i for i in risk_issues)
    assert any("critical post-baseline risk must block GA" in i for i in risk_issues)


def test_billing_contracts_deep_branches():
    rep = default_billing_readiness_report()
    assert len(rep["provider_decision_issues"]) == 0

    # SubscriptionSnapshot validation
    snap_bad = SubscriptionSnapshot(
        account_id="",
        plan=BillingPlan.PARENT,
        state=SubscriptionState.EXPIRED,
        provider_customer_id=None,
        provider_subscription_id=None,
        current_period_end_utc=None,
    )
    s_issues = snap_bad.validate()
    assert any("account_id is required" in i for i in s_issues)
    assert any("paid plans require provider_subscription_id" in i for i in s_issues)
    assert any("expired subscriptions require period end" in i for i in s_issues)


    # Decision validation errors
    bad_dec = BillingProviderDecision(
        provider=BillingProvider.STRIPE,
        adr_path="invalid/path.md",
        architecture_doc_path="invalid/path.md",
        checkout_hosted=True,
        stores_raw_card_data=True,
        webhook_signature_required=False,
        idempotency_required=False,
    )
    issues = bad_dec.validate()
    assert any("must not store raw card data" in i for i in issues)
    assert any("webhook signature verification is mandatory" in i for i in issues)
    assert any("webhook idempotency is mandatory" in i for i in issues)

    # PricingPolicy validation errors
    bad_price = PricingPolicy(
        free_tier_enabled=True,
        parent_plan_enabled=True,
        school_plan_enabled=True,
        sponsored_learner_plan_enabled=True,
        ngo_community_plan_enabled=True,
        trial_length_days=-1,
        payment_failure_grace_days=-1,
        cancellation_policy="",
        refund_policy="",
        data_access_after_cancellation_days=-1,
        invoices_enabled=False,
        receipts_enabled=False,
        coupons_enabled=True,
        sponsorships_enabled=True,
        admin_config_required=True,
    )
    p_issues = bad_price.validate()
    assert any("trial length cannot be negative" in i for i in p_issues)
    assert any("cancellation policy is required" in i for i in p_issues)
    assert any("refund policy is required" in i for i in p_issues)
    assert any("invoice support is required" in i for i in p_issues)
    assert any("receipt support is required" in i for i in p_issues)

    # State transitions
    assert validate_subscription_transition(None, SubscriptionState.TRIAL) is True
    assert validate_subscription_transition(SubscriptionState.CANCELED, SubscriptionState.ACTIVE) is False
    assert validate_subscription_transition(SubscriptionState.ACTIVE, SubscriptionState.CANCELED) is True
    assert validate_subscription_transition(SubscriptionState.EXPIRED, SubscriptionState.TRIAL) is False


    # Webhook signature branches
    secret = "whsec_test_secret_12345"
    payload = {"type": "invoice.paid", "id": "evt_1"}
    now_ts = 1700000000
    valid_sig = compute_webhook_signature(secret, now_ts, payload)

    assert verify_webhook_signature(secret=secret, header=valid_sig, payload=payload, now_timestamp=now_ts) is True
    # Expired tolerance
    assert verify_webhook_signature(secret=secret, header=valid_sig, payload=payload, now_timestamp=now_ts + 600) is False
    # Malformed headers
    assert verify_webhook_signature(secret=secret, header="bad_header", payload=payload, now_timestamp=now_ts) is False
    assert verify_webhook_signature(secret=secret, header="t=abc,v1=123", payload=payload, now_timestamp=now_ts) is False
    assert verify_webhook_signature(secret=secret, header="t=1700000000,v1=not_a_hex", payload=payload, now_timestamp=now_ts) is False

    # WebhookIdempotencyStore
    store = WebhookIdempotencyStore()
    assert store.process("evt-1", "charge.succeeded", now_ts) == "processed"
    assert store.process("evt-1", "charge.succeeded", now_ts) == "duplicate"
    with pytest.raises(ValueError, match="event_id is required"):
        store.process("", "charge.succeeded", now_ts)

    store.mark_dead_letter("evt-2", "JSON parse error")
    assert len(store.dead_letter) == 1

    # WebhookRetryPolicy
    bad_retry = WebhookRetryPolicy(max_attempts=0, backoff_seconds=(0, -5))
    r_issues = bad_retry.validate()
    assert any("max_attempts must be at least 1" in i for i in r_issues)
    assert any("backoff values must be positive" in i for i in r_issues)

    # BillingAuditEvent
    bad_audit = BillingAuditEvent(
        event_id="",
        event_type="charge",
        account_id="",
        provider=BillingProvider.STRIPE,
        occurred_at_utc=datetime.now(),  # naive
        request_id="",
        idempotency_key="",
        raw_payload_retained=True,
    )
    a_issues = bad_audit.validate()
    assert any("event_id is required" in i for i in a_issues)
    assert any("account_id is required" in i for i in a_issues)
    assert any("must be timezone-aware" in i for i in a_issues)
    assert any("must not be retained" in i for i in a_issues)


def test_diagnostics_contracts_deep_branches():
    # DiagnosticItemSpec validation failures

    bad_item = DiagnosticItemSpec(
        item_id="item-bad",
        subject="",
        grade=15,  # > 12
        topic="",
        skill="",
        difficulty=5.0,  # > 4.0
        discrimination=0.05,  # < 0.1
        correct_answer="A",
        distractors=("A", "B"),  # correct answer in distractors
        explanation="",
        caps_reference="",
        max_exposure=0,  # < 1
        exposure_count=-1,  # < 0
    )
    val_errs = validate_diagnostic_item_schema(bad_item)
    assert any("subject is required" in e for e in val_errs)
    assert any("grade must be between 0 and 12" in e for e in val_errs)
    assert any("difficulty must be in" in e for e in val_errs)
    assert any("discrimination must be in" in e for e in val_errs)
    assert any("correct answer must not appear as a distractor" in e for e in val_errs)
    assert any("max_exposure must be positive" in e for e in val_errs)
    assert any("exposure_count must be non-negative" in e for e in val_errs)

    # Item without distractors
    no_dist_item = DiagnosticItemSpec(
        item_id="item-nodist",
        subject="Math",
        grade=5,
        topic="Numbers",
        skill="Add",
        difficulty=0.0,
        discrimination=1.0,
        correct_answer="A",
        distractors=(),
        explanation="Expl",
        caps_reference="CAPS-1",
    )

    assert any("at least one distractor is required" in e for e in validate_diagnostic_item_schema(no_dist_item))

    # Fisher information selection with no eligible items
    assert select_item_by_fisher_information(0.0, []) is None
    assert select_item_by_fisher_information(0.0, [bad_item]) is None

    # Grade equivalent bounding
    ge_low = grade_equivalent_from_theta(-4.0, 5)
    ge_high = grade_equivalent_from_theta(4.0, 5)
    assert ge_low < 5.0
    assert ge_high > 5.0

    # Gap topics
    gaps = identify_gap_topics([
        {"topic": "Fractions", "correct": False},
        {"topic": "Fractions", "correct": False},
        {"topic": "Decimals", "correct": False},
        {"topic": "Algebra", "correct": True},
    ])
    assert gaps == ["Fractions", "Decimals"]

    # Review status transitions
    assert can_transition_review_status(ItemReviewStatus.DRAFT, ItemReviewStatus.AI_GENERATED) is True
    assert can_transition_review_status(ItemReviewStatus.AI_GENERATED, ItemReviewStatus.APPROVED) is False
    assert can_transition_review_status(ItemReviewStatus.HUMAN_REVIEWED, ItemReviewStatus.APPROVED) is True

    # Audit minimum viable item bank
    approved_good = DiagnosticItemSpec(
        item_id="item-app-1",
        subject="Mathematics",
        grade=5,
        topic="Numbers",
        skill="Add",
        difficulty=0.0,
        discrimination=1.0,
        correct_answer="A",
        distractors=("B", "C"),
        explanation="Expl",
        caps_reference="CAPS-1",
        review_status=ItemReviewStatus.APPROVED,
    )
    audit_errs = audit_minimum_viable_item_bank(
        [approved_good],
        launch_grades=[5, 6],
        launch_subjects=["Mathematics"],
        min_items_per_grade_subject=1,
    )
    assert any("grade 6" in e for e in audit_errs)

    # Bias dimensions
    dims = required_bias_review_dimensions()
    assert BiasDimension.LANGUAGE in dims
    assert BiasDimension.REGION in dims
    assert BiasDimension.SOCIOECONOMIC_CONTEXT in dims

    # Misconceptions remediation tags
    item_with_tags = DiagnosticItemSpec(
        item_id="item-tag-1",
        subject="Mathematics",
        grade=5,
        topic="Numbers",
        skill="Add",
        difficulty=0.0,
        discrimination=1.0,
        correct_answer="A",
        distractors=("B",),
        explanation="Expl",
        caps_reference="CAPS-1",
        misconception_tags=(" PlaceValue ", " regrouping "),
    )
    tags = remediation_tags_from_misconceptions(item_with_tags)
    assert tags == ("placevalue", "regrouping")

