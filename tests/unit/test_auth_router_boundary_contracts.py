from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

from app.services.auth_runtime_boundary import AuthRuntimeContext


ROOT = Path(__file__).resolve().parents[2]


class FakeLearner:
    def __init__(self, learner_id: str):
        self.id = learner_id


class FakeLearnerRepo:
    async def get_by_guardian(self, guardian_id):
        assert guardian_id == "guardian-1"
        return [FakeLearner("learner-1"), {"id": "learner-2"}]


def test_auth_runtime_context_extracts_guardian_learner_ids():
    async def run():
        context = AuthRuntimeContext(db=None, learner_repo=FakeLearnerRepo())
        assert await context.guardian_learner_ids("guardian-1") == ["learner-1", "learner-2"]

    asyncio.run(run())


def test_auth_router_no_longer_uses_direct_learner_repository():
    source = (ROOT / "app/api_v2_routers/auth.py").read_text(encoding="utf-8")
    assert "app.api_v2_deps.auth_runtime" in source
    assert "LearnerRepository" not in source
    assert "LearnerRepository(" not in source
    assert ".get_by_guardian(" not in source


def test_auth_boundary_scripts_run():
    for command in [
        [sys.executable, "scripts/inspect_auth_router_boundary.py"],
        [sys.executable, "scripts/check_auth_router_boundary.py"],
        [sys.executable, "scripts/generate_auth_boundary_debt_report.py"],
    ]:
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        assert result.returncode == 0, result.stdout


def test_makefile_contains_auth_boundary_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-router-boundary-inspect:" in text
    assert "auth-router-boundary-repair:" in text
    assert "backend-implementation-721-750-full-check:" in text
