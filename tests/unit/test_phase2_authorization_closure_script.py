from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_phase2_authorization_closure import COMMANDS


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_phase2_authorization_closure_script_exists() -> None:
    assert (REPO_ROOT / "scripts" / "check_phase2_authorization_closure.py").exists()


@pytest.mark.unit
def test_phase2_authorization_closure_command_set_includes_required_guards() -> None:
    rendered = "\n".join(" ".join(command) for command in COMMANDS)

    assert "make runtime-check" in rendered
    assert "make openapi-check" in rendered
    assert "make route-inventory-check" in rendered
    assert "make pr002r-check" in rendered
    assert "make phase2-authz-check" in rendered
    assert "make learner-authz-check" in rendered
    assert "tests/unit/test_phase2_router_import_smoke.py" in rendered


@pytest.mark.unit
def test_makefile_exposes_phase2_authorization_closure_target() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "phase2-authz-closure:" in makefile
    assert "scripts/check_phase2_authorization_closure.py" in makefile
