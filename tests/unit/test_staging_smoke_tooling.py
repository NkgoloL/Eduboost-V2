from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_module():
    path = ROOT / "scripts/run_staging_smoke.py"
    spec = importlib.util.spec_from_file_location("run_staging_smoke_for_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_staging_smoke_for_test"] = module
    spec.loader.exec_module(module)
    return module


def test_normalize_base_url_requires_http_scheme():
    module = _load_module()
    assert module._normalize_base_url("https://example.test") == "https://example.test/"

    try:
        module._normalize_base_url("example.test")
    except ValueError as exc:
        assert "http" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_write_outputs_and_validate_payload(tmp_path):
    module = _load_module()
    payload = {
        "captured_at": "2026-05-16T00:00:00Z",
        "base_url": "https://staging.example.test",
        "passed": True,
        "results": [
            {
                "name": "health_deep",
                "method": "GET",
                "path": "/api/v2/health/deep",
                "expected_statuses": [200],
                "actual_status": 200,
                "passed": True,
                "duration_ms": 12.3,
                "error": None,
                "headers": {"content-type": "application/json"},
            }
        ],
    }
    json_path = tmp_path / "staging_smoke_latest.json"
    md_path = tmp_path / "staging_smoke_evidence.md"

    module.write_outputs(payload, json_path=json_path, markdown_path=md_path)

    assert json.loads(json_path.read_text(encoding="utf-8"))["passed"] is True
    assert "runtime smoke passed" in md_path.read_text(encoding="utf-8")
    assert module.validate_payload(json_path) is True


def test_makefile_contains_staging_smoke_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "staging-smoke:" in text
    assert "staging-smoke-check:" in text



def test_placeholder_staging_url_is_rejected():
    module = _load_module()
    assert module._is_placeholder_base_url("https://staging.example.com") is True
    assert module._is_placeholder_base_url("https://real-staging.eduboost.test") is True
    assert module._is_placeholder_base_url("https://staging.eduboost.internal") is False


def test_validate_payload_can_require_pass(tmp_path):
    module = _load_module()
    path = tmp_path / "staging_smoke_latest.json"
    path.write_text(
        json.dumps(
            {
                "captured_at": "2026-05-16T00:00:00Z",
                "base_url": "https://staging.eduboost.internal",
                "passed": False,
                "results": [
                    {
                        "name": "health_deep",
                        "method": "GET",
                        "path": "/api/v2/health/deep",
                        "expected_statuses": [200],
                        "actual_status": None,
                        "passed": False,
                        "duration_ms": 1.0,
                        "error": "network",
                        "headers": {},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    assert module.validate_payload(path) is True
    assert module.validate_payload(path, require_pass=True) is False


def test_smoke_runner_writes_latest_markdown_not_release_gate():
    module = _load_module()
    assert module.DEFAULT_MARKDOWN.name == "staging_smoke_latest.md"
