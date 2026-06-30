from __future__ import annotations
from scripts.jwt_secret_rotation_evidence import _short_fingerprint, has_placeholder, issue_hs256_jwt, run_token_self_test, verify_hs256_jwt

def test_placeholder_detection():
    assert has_placeholder("<secret>")
    assert has_placeholder("change-me-now")
    assert not has_placeholder("A-realistic-high-entropy-value-1234567890")

def test_fingerprint_is_redacted_prefix():
    fp = _short_fingerprint("A-realistic-high-entropy-value-1234567890")
    assert len(fp) == 16

def test_hs256_issue_and_verify():
    secret = "A-realistic-high-entropy-value-1234567890"
    token = issue_hs256_jwt(secret, token_use="access")
    assert verify_hs256_jwt(token, secret, expected_use="access")
    assert not verify_hs256_jwt(token, secret, expected_use="refresh")

def test_token_self_test_requires_separate_secrets():
    status = run_token_self_test("A-realistic-high-entropy-access-value-1234567890", "A-realistic-high-entropy-refresh-value-1234567890")
    assert status.access_issue_verify
    assert status.refresh_issue_verify
    assert status.access_tamper_rejected
    assert status.refresh_tamper_rejected
    assert status.access_refresh_separated
    assert not status.blockers
