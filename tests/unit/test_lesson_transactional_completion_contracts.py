from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from app.services.lesson_transactional_completion import (
    LessonCompletionInput,
    LessonCompletionNotFoundError,
    LessonCompletionResult,
    LessonCompletionTransactionError,
    TransactionalLessonCompletionService,
)


ROOT = Path(__file__).resolve().parents[2]


def test_lesson_transactional_completion_exports_expected_symbols():
    assert LessonCompletionInput
    assert LessonCompletionNotFoundError
    assert LessonCompletionResult
    assert LessonCompletionTransactionError
    assert TransactionalLessonCompletionService


def test_lesson_transactional_completion_uses_explicit_transaction_boundary():
    source = (ROOT / "app/services/lesson_transactional_completion.py").read_text(encoding="utf-8")

    assert "async with self.session.begin()" in source
    assert "fail_after_lesson" in source
    assert "fail_after_xp" in source
    assert "fail_after_audit" in source


def test_lesson_gamification_transaction_rollback_checker_runs():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_lesson_gamification_transaction_rollback_proof.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_makefile_contains_lesson_gamification_transaction_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "lesson-gamification-transaction-rollback-proof-test:" in source
    assert "lesson-gamification-transaction-rollback-proof-check:" in source
    assert "backend-implementation-1551-1590-full-check:" in source
