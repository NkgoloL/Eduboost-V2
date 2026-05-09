"""Tests for shared pytest import-path configuration."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_repo_root_is_available_on_pytest_sys_path() -> None:
    assert str(REPO_ROOT) in sys.path


@pytest.mark.unit
def test_app_package_imports_without_per_test_sys_path_patch() -> None:
    from app.api_v2 import app

    assert app.title == "EduBoost SA V2"
