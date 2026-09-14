from scripts.coverage_suites.coverage_contract import (
    coverage_commands,
    evaluate_coverage_contract,
    evaluate_measured_coverage,
    evaluate_threshold_alignment,
)


def test_coverage_contract_is_valid_for_authority_state():
    result = evaluate_coverage_contract(require_freshness=False)
    assert result["valid"] is True
    assert result["taxonomy_classes_match"] is True
    assert result["domain_contracts_valid"] is True
    assert result["no_presence_only_release_policy"] is True


def test_coverage_thresholds_are_documentation_aligned_and_do_not_swallow_failures():
    result = evaluate_threshold_alignment()
    assert result["valid"] is True
    assert result["minimum_line_coverage_percent"] >= 90
    assert result["makefile_coverage_threshold"] >= 90
    assert result["test_coverage_target_swallows_failures"] is False
    assert result["coveragerc_branch_enabled"] is True


def test_each_coverage_class_has_a_command():
    commands = coverage_commands()
    assert {item["coverage_class"] for item in commands} == {"product", "runtime", "governance", "advisory"}
    assert any(item["requires_live_stack"] for item in commands if item["coverage_class"] == "runtime")


def test_evaluate_measured_coverage_with_mock_xml(tmp_path):
    mock_xml = tmp_path / "coverage.xml"
    mock_xml.write_text("""<?xml version="1.0" ?>
<coverage version="7.5.0" timestamp="1726000000" lines-valid="100" lines-covered="95" line-rate="0.952" branches-valid="20" branches-covered="18" branch-rate="0.900" complexity="0">
</coverage>
""")
    result = evaluate_measured_coverage(report_path=mock_xml, min_percent=90.0)
    assert result["valid"] is True
    assert result["line_coverage_percent"] == 95.2
    assert result["branch_coverage_percent"] == 90.0

    fail_result = evaluate_measured_coverage(report_path=mock_xml, min_percent=96.0)
    assert fail_result["valid"] is False

    missing_result = evaluate_measured_coverage(report_path=tmp_path / "nonexistent.xml")
    assert missing_result["valid"] is False
    assert "not found" in missing_result["error"]
