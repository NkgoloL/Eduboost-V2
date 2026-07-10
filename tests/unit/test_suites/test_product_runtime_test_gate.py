from scripts.test_suites.product_runtime_gate import (
    REQUIRED_PRODUCT_DOMAINS,
    REQUIRED_RUNTIME_DOMAINS,
    evaluate_product_runtime_gate_contract,
    gate_commands,
)


def test_product_runtime_gate_contract_is_valid():
    result = evaluate_product_runtime_gate_contract()
    assert result["valid"] is True
    assert not result["missing_product_domains"]
    assert not result["missing_runtime_domains"]


def test_product_and_runtime_domains_require_negative_evidence():
    result = evaluate_product_runtime_gate_contract()
    assert set(result["required_product_domains"]) == set(REQUIRED_PRODUCT_DOMAINS)
    assert set(result["required_runtime_domains"]) == set(REQUIRED_RUNTIME_DOMAINS)
    assert result["product_domains_valid"] is True
    assert result["runtime_domains_valid"] is True
    assert result["release_policy_valid"] is True


def test_gate_commands_are_release_blocking_without_self_proving_release():
    commands = gate_commands()
    assert {command["gate_class"] for command in commands} >= {"product", "runtime", "combined"}
    assert all(command["release_blocking"] is True for command in commands)
