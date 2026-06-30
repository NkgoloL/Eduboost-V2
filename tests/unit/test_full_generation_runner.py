"""Unit tests for full generation runner."""
from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.mark.unit
def test_runner_script_exists() -> None:
    """Runner script exists."""
    runner_path = Path(__file__).parent.parent.parent / "scripts" / "content_factory" / "run_full_generation.py"
    assert runner_path.exists()
    assert runner_path.is_file()


@pytest.mark.unit
def test_runner_script_is_executable() -> None:
    """Runner script is executable."""
    runner_path = Path(__file__).parent.parent.parent / "scripts" / "content_factory" / "run_full_generation.py"
    assert os.access(runner_path, os.X_OK)


@pytest.mark.unit
def test_runner_script_has_main_guard() -> None:
    """Runner script has if __name__ == '__main__' guard."""
    runner_path = Path(__file__).parent.parent.parent / "scripts" / "content_factory" / "run_full_generation.py"
    content = runner_path.read_text()
    assert 'if __name__ == "__main__":' in content

