from __future__ import annotations

from scripts.runtime.disposable_stack_lineage import (
    LineageProbeConfig,
    build_lineage_reconciliation_decision,
    verify_compose_file_contract,
    verify_disposable_stack_lineage_contract,
    verify_migration_graph_contract,
)


def test_disposable_stack_contract_is_installed() -> None:
    result = verify_disposable_stack_lineage_contract(require_live=False)
    assert result["contract_valid"] is True
    assert result["valid"] is True
    assert result["checks"]["policy"]["no_blind_alembic_stamp"] is True
    assert result["checks"]["policy"]["snapshot_before_lineage_repair"] is True


def test_live_lineage_is_not_claimed_without_database_url() -> None:
    result = verify_disposable_stack_lineage_contract(
        require_live=False,
        config=LineageProbeConfig(database_url=None),
    )
    assert result["checks"]["lineage_probe"]["status"] == "blocked"
    assert result["live_lineage_schema_green"] is False
    assert "provide live disposable stack evidence" in result["next_required_runtime_action"]


def test_require_live_mode_fails_without_database_url() -> None:
    result = verify_disposable_stack_lineage_contract(
        require_live=True,
        config=LineageProbeConfig(database_url=None),
    )
    assert result["contract_valid"] is True
    assert result["valid"] is False
    assert result["live_lineage_schema_required"] is True
    assert result["checks"]["lineage_probe"]["status"] == "blocked"


def test_explicit_invalid_database_url_is_failed_live_evidence() -> None:
    result = verify_disposable_stack_lineage_contract(
        require_live=False,
        config=LineageProbeConfig(database_url="postgresql://invalid:invalid@127.0.0.1:1/invalid"),
    )

    assert result["contract_valid"] is True
    assert result["checks"]["lineage_probe"]["status"] == "fail"
    assert result["live_lineage_schema_green"] is False


def test_compose_and_migration_contracts_are_static_green() -> None:
    compose = verify_compose_file_contract()
    graph = verify_migration_graph_contract()
    assert compose["valid"] is True
    assert not compose["missing_services"]
    assert graph["valid"] is True
    assert graph["expected_single_head"] == "20260711_1510_prd11_runtime_green_exec5"


def test_unknown_revision_decision_forbids_blind_stamp() -> None:
    probe = {
        "status": "fail",
        "lineage": {"unknown_revisions": ["20260531_1600"]},
        "schema_contract": {"missing_tables": ["runtime_kg_nodes"], "missing_columns": {}},
    }
    decision = build_lineage_reconciliation_decision(probe)
    assert decision["status"] == "fail"
    assert decision["unknown_live_revision"] is True
    assert decision["blind_stamp_allowed"] is False
    assert "snapshot" in decision["safe_next_action"]
