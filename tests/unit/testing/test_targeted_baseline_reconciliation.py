from __future__ import annotations

from scripts.testing.targeted_baseline_reconciliation import (
    TEST_ENVIRONMENT,
    assert_archival_or_current_valid,
    assert_release_boundaries_closed,
    sanitized_test_environment,
    verify_environment_contract,
)


def test_sanitized_environment_overrides_release_contamination() -> None:
    env = sanitized_test_environment({"DEBUG": "release", "APP_ENV": "production", "ENVIRONMENT": "prod"})
    assert not verify_environment_contract(env)
    assert {key: env[key] for key in TEST_ENVIRONMENT} == TEST_ENVIRONMENT


def test_archival_assertion_accepts_valid_current_record() -> None:
    result = {"authority_valid": True, "valid": True, "errors": [], "production_release_authorised": False}
    assert_archival_or_current_valid(result)
    assert_release_boundaries_closed(result)
