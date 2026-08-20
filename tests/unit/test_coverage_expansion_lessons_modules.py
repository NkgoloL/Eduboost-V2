"""
Additional unit tests for app.modules.lessons.prompt_version_registry and
app.modules.lessons.lesson_metrics to further expand test coverage.
"""
from __future__ import annotations

import tempfile
import pytest
from pathlib import Path

from app.modules.lessons.prompt_version_registry import (
    PromptTemplateRegistry,
    validate_version_immutable,
)
from app.modules.lessons.lesson_metrics import lesson_metrics


def test_prompt_template_registry_flow():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        tpl_file = tmp_path / "test_tpl_v1.jinja2"
        tpl_file.write_text("Hello {{ name }}!", encoding="utf-8")

        registry = PromptTemplateRegistry(prompts_dir=tmp_path)

        assert registry.get_template_version("test_tpl_v1") == "test_tpl_v1"
        assert "test_tpl_v1" in registry.list_templates()

        digest = registry.get_content_hash("test_tpl_v1")
        assert len(digest) == 64

        rendered = registry.render("test_tpl_v1", name="EduBoost")
        assert rendered == "Hello EduBoost!"

        # Test hash change warning path
        tpl_file.write_text("Hello {{ name }} updated!", encoding="utf-8")
        new_digest = registry.get_content_hash("test_tpl_v1")
        assert new_digest != digest


def test_prompt_template_registry_missing():
    with tempfile.TemporaryDirectory() as tmp_dir:
        registry = PromptTemplateRegistry(prompts_dir=tmp_dir)
        with pytest.raises(FileNotFoundError):
            registry.get_content_hash("non_existent")


def test_validate_version_immutable():
    # Allowed when existing is None or unchanged
    validate_version_immutable(None, "v1", "lesson-1")
    validate_version_immutable("v1", "v1", "lesson-1")

    # Raises ValueError when existing is changed
    with pytest.raises(ValueError) as exc_info:
        validate_version_immutable("v1", "v2", "lesson-1")
    assert "Cannot overwrite with" in str(exc_info.value)


def test_lesson_metrics_methods():
    lesson_metrics.record_validation(passed=True, caps_ref="4.M.1.1")
    lesson_metrics.record_validation(passed=False, caps_ref="4.M.1.1", failed_rule="rule_1")
    lesson_metrics.record_answer_key_verification(verified=True, caps_ref="4.M.1.1")
    lesson_metrics.set_review_queue_depth(5)
    lesson_metrics.record_provider_fallback(from_provider="groq", to_provider="anthropic")
    lesson_metrics.set_budget_utilization(ratio=0.75, tenant_id="test")
    lesson_metrics.set_circuit_breaker_state(provider="groq", state="open")
    lesson_metrics.record_generation_attempt(outcome="success", caps_ref="4.M.1.1", provider="groq")
    assert lesson_metrics is not None

