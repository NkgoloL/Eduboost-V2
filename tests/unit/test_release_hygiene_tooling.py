from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_test_environment_check_accepts_json_and_comma_origins(monkeypatch):
    module = _load_module(ROOT / "scripts/check_test_environment.py", "check_test_environment_for_test")

    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./eduboost_test.db")
    monkeypatch.setenv("ENCRYPTION_KEY", "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=")
    monkeypatch.setenv("JWT_SECRET", "local-test-secret-value")
    monkeypatch.setenv("ALLOWED_ORIGINS", '["http://localhost:3000","http://test"]')
    assert all(result.passed for result in module.run_checks(strict=True))

    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000,http://test")
    assert all(result.passed for result in module.run_checks(strict=True))


def test_route_alias_matrix_renderer_marks_alias_presence():
    module = _load_module(ROOT / "scripts/generate_route_alias_matrix.py", "generate_route_alias_matrix_for_test")
    routes = {
        ("GET", "/api/v2/health"),
        ("GET", "/v2/health"),
        ("POST", "/api/v2/lessons/generate"),
    }
    rows = module.collect_rows(routes)
    rendered = module.render_markdown(rows)

    assert "`/api/v2/health`" in rendered
    assert "`/v2/health`" in rendered
    assert "present" in rendered
    assert "`/api/v2/lessons/generate`" in rendered
    assert "missing" in rendered


def test_release_evidence_index_check_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_release_evidence_index.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_makefile_contains_release_hygiene_targets():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "test-env-check:" in makefile
    assert "route-alias-matrix:" in makefile
    assert "release-evidence-index-check:" in makefile
