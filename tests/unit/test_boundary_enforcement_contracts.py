from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from app.api_v2_deps.consent_lifecycle import authenticated_actor_id

ROOT = Path(__file__).resolve().parents[2]


def test_authenticated_actor_id_supports_dict_and_object():
    assert authenticated_actor_id({"id": "user-1"}) == "user-1"

    class User:
        user_id = "user-2"

    assert authenticated_actor_id(User()) == "user-2"


def test_popia_router_uses_dependency_module_not_repository_imports():
    source = (ROOT / "app/api_v2_routers/popia.py").read_text(encoding="utf-8")
    assert "app.api_v2_deps.consent_lifecycle" in source
    assert "from app.repositories" not in source
    assert "from app.core.database import get_db" not in source
    assert "from sqlalchemy.ext.asyncio import AsyncSession" not in source


def test_lessons_router_has_no_repository_imports_after_object_auth_repair():
    source = (ROOT / "app/api_v2_routers/lessons.py").read_text(encoding="utf-8")
    assert "from app.repositories" not in source
    assert "app.services.lesson_authorization" in source


def test_boundary_scripts_run():
    for command in [
        [sys.executable, "scripts/generate_router_boundary_matrix.py"],
        [sys.executable, "scripts/check_router_boundary_enforcement.py"],
        [sys.executable, "scripts/check_import_linter_availability.py"],
        [sys.executable, "scripts/generate_service_boundary_inventory.py"],
        [sys.executable, "scripts/generate_legacy_learner_access_guard_report.py"],
    ]:
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        assert result.returncode == 0, result.stdout


def test_makefile_contains_boundary_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "router-boundary-matrix:" in text
    assert "router-boundary-check:" in text
    assert "backend-implementation-651-670-full-check:" in text
