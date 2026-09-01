from app.modules.production_release import (
    build_default_true_state_runtime_baseline_report,
    build_green_true_state_runtime_baseline_report,
)
from scripts.production_readiness.collect_prd1100r_true_state_runtime_baseline import collect_baseline


def test_default_true_state_runtime_baseline_records_operational_hold():
    payload = build_default_true_state_runtime_baseline_report().to_payload()

    assert payload["prd_id"] == "PRD-11.0R"
    assert payload["accepted"] is True
    assert payload["runtime_baseline_green"] is False
    assert payload["controlled_beta_live_traffic_authorised"] is True
    assert payload["live_learner_traffic_authorised"] is True
    assert payload["controlled_beta_activation_operational_hold"] is True
    assert payload["live_learner_traffic_operationally_safe"] is False
    assert payload["production_release_evidence_blocked_until_runtime_baseline_green"] is True
    assert payload["production_release_authorised"] is False
    assert payload["deployment_authorised"] is False
    assert payload["public_beta_authorised"] is False
    assert payload["billing_launch_authorised"] is False


def test_green_true_state_runtime_baseline_is_explicitly_different():
    payload = build_green_true_state_runtime_baseline_report().to_payload()

    assert payload["runtime_baseline_green"] is True
    assert payload["controlled_beta_activation_operational_hold"] is False
    assert payload["live_learner_traffic_operationally_safe"] is True
    assert payload["production_release_evidence_blocked_until_runtime_baseline_green"] is False
    assert payload["production_release_authorised"] is False


def test_collector_fails_closed_without_runtime_dependencies(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SQLALCHEMY_DATABASE_URI", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)

    result = collect_baseline(run_expensive_checks=False)

    assert result["prd_id"] == "PRD-11.0R"
    assert result["runtime_baseline_green"] is False
    assert result["operational_hold_required"] is True
    assert "database_lineage_and_schema" in result["blockers"]
    assert "redis_readiness_dependency" in result["blockers"]
    assert result["checks"]["database_lineage_and_schema"]["status"] == "blocked"
    assert result["checks"]["redis_readiness_dependency"]["status"] == "blocked"


def test_true_state_runtime_baseline_custom_parameters():
    from app.modules.production_release.true_state_baseline import TrueStateRuntimeBaselineReport

    report = TrueStateRuntimeBaselineReport(
        accepted=True,
        prd_id="PRD-11.0R-CUSTOM",
        report_scope="custom_scope",
        concern_categories=("cat1", "cat2"),
        blockers=("custom_blocker",),
        runtime_baseline_green=True,
        runtime_baseline_status="green_custom",
        controlled_beta_activation_operational_hold=False,
        live_learner_traffic_operationally_safe=True,
        production_release_evidence_blocked_until_runtime_baseline_green=False,
        next_action="proceed_custom",
    )
    p = report.to_payload()
    assert p["prd_id"] == "PRD-11.0R-CUSTOM"
    assert p["concern_categories"] == ["cat1", "cat2"]
    assert p["blockers"] == ["custom_blocker"]
    assert p["runtime_baseline_green"] is True
