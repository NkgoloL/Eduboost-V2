from __future__ import annotations

from scripts.diag_deep_health_runtime_evidence import has_placeholder, infer_component_signals, is_deep_health_url, valid_https_url, write_status

def test_valid_https_url_rejects_placeholders_and_localhost():
    assert valid_https_url("https://staging.eduboost.internal/api/v2/health/deep")
    assert not valid_https_url("http://staging.eduboost.internal/api/v2/health/deep")
    assert not valid_https_url("https://example.com/api/v2/health/deep")
    assert not valid_https_url("http://localhost:8000/api/v2/health/deep")
    assert not valid_https_url("<deep-health-url>")

def test_deep_health_url_requires_deep_endpoint():
    assert is_deep_health_url("https://staging.eduboost.internal/api/v2/health/deep")
    assert is_deep_health_url("https://staging.eduboost.internal/deep")
    assert not is_deep_health_url("https://staging.eduboost.internal/api/v2/system/health")

def test_placeholder_detection():
    assert has_placeholder("REAL_DEEP_HEALTH_URL")
    assert has_placeholder("https://example.com")
    assert not has_placeholder("https://staging.eduboost.internal")

def test_infer_component_signals_from_json_body():
    body = '{"database":{"status":"ok"},"migrations":{"status":"passed"},"audit":{"status":"healthy"},"diagnostic_session":{"status":"success"}}'
    signals = infer_component_signals(body)
    assert signals["db"] == "passed"
    assert signals["migration"] == "passed"
    assert signals["audit"] == "passed"
    assert signals["session"] == "passed"

def test_status_writes_not_accepted_without_runtime_inputs():
    status = write_status(run_http=False)
    assert status.status in {"diag-deep-health-runtime-accepted", "diag-deep-health-runtime-not-accepted"}
