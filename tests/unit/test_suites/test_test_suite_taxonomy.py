from __future__ import annotations

from scripts.test_suites.test_suite_taxonomy import (
    DEFAULT_SUITE_COMMANDS,
    classify_test_path,
    evaluate_governance_sync,
    evaluate_taxonomy,
    load_pytest_markers,
)


def test_pytest_markers_include_four_prd11_test_classes() -> None:
    markers = load_pytest_markers()
    assert {"product", "runtime", "governance", "advisory"}.issubset(markers)


def test_taxonomy_records_full_capabilities_for_each_class() -> None:
    result = evaluate_taxonomy()
    assert result["valid"] is True
    assert result["missing_classes"] == []
    assert result["missing_markers"] == []
    assert result["class_capabilities_valid"] is True
    assert result["governance_sync"]["state_agrees"] is True


def test_governance_sync_checks_freshness_and_release_boundaries() -> None:
    sync = evaluate_governance_sync()
    assert sync["valid"] is True
    assert sync["fresh"] is True
    assert sync["freshness_max_age_days"] == 21
    assert sync["release_boundaries_locked"] is True


def test_suite_commands_are_explicitly_classed() -> None:
    classes = {command.suite_class for command in DEFAULT_SUITE_COMMANDS}
    assert classes == {"product", "runtime", "governance", "advisory"}
    blocking = {command.suite_class: command.release_blocking for command in DEFAULT_SUITE_COMMANDS}
    assert blocking["product"] is True
    assert blocking["runtime"] is True
    assert blocking["governance"] is False
    assert blocking["advisory"] is True


def test_path_classifier_keeps_governance_separate_from_product() -> None:
    assert classify_test_path("tests/unit/roadmap_reconciliation/test_prd.py") == "governance"
    assert classify_test_path("tests/integration/test_ready.py") == "runtime"
    assert classify_test_path("tests/unit/test_openapi_drift.py") == "advisory"
    assert classify_test_path("tests/unit/modules/lessons/test_service.py") == "product"
