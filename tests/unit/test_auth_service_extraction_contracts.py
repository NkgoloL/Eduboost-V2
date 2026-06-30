from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

from app.services.auth_application_service import AuthApplicationService, AuthRepositoryBundle, extract_identifier


ROOT = Path(__file__).resolve().parents[2]


class FakeRepo:
    def __init__(self, db=None):
        self.db = db


class FakeLearnerRepo:
    async def get_by_guardian(self, guardian_id):
        assert guardian_id == "guardian-1"
        return [{"id": "learner-1"}, type("Learner", (), {"id": "learner-2"})()]


class FakeBundle(AuthRepositoryBundle):
    @property
    def learner_repo(self):
        return FakeLearnerRepo()


def test_auth_application_service_preserves_guardian_learner_scope_lookup():
    import asyncio

    async def run():
        service = AuthApplicationService(db=object(), repositories=FakeBundle(db=object()))
        assert await service.guardian_learner_ids("guardian-1") == ["learner-1", "learner-2"]

    asyncio.run(run())


def test_extract_identifier_supports_dict_object_and_scalar():
    assert extract_identifier({"id": "x"}) == "x"
    assert extract_identifier(type("Obj", (), {"learner_id": "y"})()) == "y"
    assert extract_identifier("z") == "z"


def test_auth_router_repository_boundary_is_closed():
    source = (ROOT / "app/api_v2_routers/auth.py").read_text(encoding="utf-8")
    assert "from app.repositories" not in source
    for token in ("UserRepository(", "GuardianRepository(", "LearnerRepository(", "ConsentRepository("):
        assert token not in source
    assert "from __future__ import annotations" not in source
    assert "app.api_v2_deps.auth_service" in source


def test_app_api_v2_imports_after_auth_service_extraction():
    api_v2 = importlib.import_module("app.api_v2")
    app = api_v2.app
    assert len(getattr(app, "routes", [])) > 0


def test_auth_service_extraction_scripts_run():
    for command in [
        [sys.executable, "scripts/generate_auth_service_extraction_report.py"],
        [sys.executable, "scripts/check_auth_service_extraction.py"],
    ]:
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        assert result.returncode == 0, result.stdout


def test_makefile_contains_871_910_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-service-extraction-repair:" in text
    assert "auth-service-extraction-check:" in text
    assert "backend-implementation-871-910-full-check:" in text
