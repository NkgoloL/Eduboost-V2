from scripts.script_suites.script_taxonomy import classify_script_path, evaluate_taxonomy, inventory_scripts


def test_script_taxonomy_is_valid() -> None:
    result = evaluate_taxonomy()
    assert result["valid"] is True
    assert set(result["required_classes"]) == {"product", "runtime", "governance", "advisory"}
    assert set(result["required_roles"]) == {"audit", "verify", "capture", "collect", "generate", "apply", "maintenance"}
    assert result["script_outputs_cannot_self_prove_release_readiness"] is True


def test_script_inventory_contains_all_classes_and_roles() -> None:
    inventory = inventory_scripts()
    assert len(inventory) > 100
    assert {item["script_class"] for item in inventory} >= {"product", "runtime", "governance", "advisory"}
    assert {item["functional_role"] for item in inventory} >= {"audit", "verify", "capture", "collect", "generate", "apply", "maintenance"}


def test_script_classification_examples() -> None:
    assert classify_script_path("scripts/roadmap_reconciliation/verify_example.py")["script_class"] == "governance"
    assert classify_script_path("scripts/production_readiness/collect_ready_probe.py")["functional_role"] == "collect"
    assert classify_script_path("scripts/check_openapi_drift.py")["script_class"] == "advisory"
    assert classify_script_path("scripts/billing/create_checkout_dry_run.py")["script_class"] == "product"
