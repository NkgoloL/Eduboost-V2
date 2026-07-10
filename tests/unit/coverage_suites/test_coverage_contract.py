from scripts.coverage_suites.coverage_contract import evaluate_coverage_contract, evaluate_threshold_alignment, coverage_commands


def test_coverage_contract_is_valid_for_authority_state():
    result = evaluate_coverage_contract()
    assert result["valid"] is True
    assert result["taxonomy_classes_match"] is True
    assert result["domain_contracts_valid"] is True
    assert result["no_presence_only_release_policy"] is True


def test_coverage_thresholds_are_documentation_aligned_and_do_not_swallow_failures():
    result = evaluate_threshold_alignment()
    assert result["valid"] is True
    assert result["minimum_line_coverage_percent"] >= 70
    assert result["makefile_coverage_threshold"] >= 70
    assert result["test_coverage_target_swallows_failures"] is False
    assert result["coveragerc_branch_enabled"] is True


def test_each_coverage_class_has_a_command():
    commands = coverage_commands()
    assert {item["coverage_class"] for item in commands} == {"product", "runtime", "governance", "advisory"}
    assert any(item["requires_live_stack"] for item in commands if item["coverage_class"] == "runtime")
