from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_popia_router_boundary_is_dependency_layered():
    source = (ROOT / "app/api_v2_routers/popia.py").read_text(encoding="utf-8")
    assert "app.api_v2_deps.consent_lifecycle" in source
    assert "from app.repositories" not in source
    assert "from app.core.database import get_db" not in source
    assert "from sqlalchemy.ext.asyncio import AsyncSession" not in source


def test_lessons_router_boundary_uses_authorization_service():
    source = (ROOT / "app/api_v2_routers/lessons.py").read_text(encoding="utf-8")
    assert "app.services.lesson_authorization" in source
    assert "from app.repositories" not in source


def test_import_linter_contract_file_exists():
    text = (ROOT / ".importlinter").read_text(encoding="utf-8")
    assert "api_v2_routers_do_not_import_repositories" in text
    assert "popia_router_uses_dependency_layer" in text
    assert "lessons_router_uses_authorization_service_layer" in text


def test_architecture_boundary_scripts_run():
    for command in [
        [sys.executable, "scripts/generate_service_family_map.py"],
        [sys.executable, "scripts/generate_router_service_dependency_map.py"],
        [sys.executable, "scripts/check_architecture_boundary_contracts.py"],
        [sys.executable, "scripts/run_import_linter_contracts.py"],
    ]:
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        assert result.returncode == 0, result.stdout


def test_makefile_contains_architecture_boundary_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "architecture-boundary-contracts-check:" in text
    assert "service-family-map:" in text
    assert "backend-implementation-671-690-full-check:" in text
