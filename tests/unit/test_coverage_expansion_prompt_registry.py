"""
Unit tests for app.services.prompt_registry:
  - PromptTemplate (render_user, prompt_version_tag)
  - PromptRegistry (register, get, list_versions, list_content_types, default)
  - get_prompt_registry singleton
"""
from __future__ import annotations

import pytest

from app.services.prompt_registry import (
    PromptRegistry,
    PromptTemplate,
    get_prompt_registry,
)


def make_template(
    id: str = "test_tpl",
    version: str = "1.0",
    content_type: str = "test_type",
    **extra,
) -> PromptTemplate:
    return PromptTemplate(
        id=id,
        version=version,
        content_type=content_type,
        schema_version="1.0",
        system="You are a test assistant.",
        user_template="Question: {question}\nGrade: {grade}",
        **extra,
    )


# ---------------------------------------------------------------------------
# PromptTemplate
# ---------------------------------------------------------------------------

class TestPromptTemplate:
    def test_render_user_success(self):
        tpl = make_template()
        rendered = tpl.render_user(question="What is 2+2?", grade=4)
        assert "What is 2+2?" in rendered
        assert "4" in rendered

    def test_render_user_missing_placeholder_raises(self):
        tpl = make_template()
        with pytest.raises(ValueError, match="requires placeholder"):
            tpl.render_user(question="What is 2+2?")  # missing grade

    def test_prompt_version_tag(self):
        tpl = make_template(id="lesson", version="2.0")
        assert tpl.prompt_version_tag == "lesson@2.0"


# ---------------------------------------------------------------------------
# PromptRegistry
# ---------------------------------------------------------------------------

class TestPromptRegistry:
    def test_register_and_get(self):
        reg = PromptRegistry()
        tpl = make_template()
        reg.register(tpl)
        retrieved = reg.get("test_type")
        assert retrieved is tpl

    def test_get_specific_version(self):
        reg = PromptRegistry()
        tpl1 = make_template(version="1.0")
        tpl2 = make_template(version="2.0")
        reg.register(tpl1)
        reg.register(tpl2)
        assert reg.get("test_type", version="1.0") is tpl1
        assert reg.get("test_type", version="2.0") is tpl2

    def test_get_latest_when_no_version(self):
        reg = PromptRegistry()
        tpl1 = make_template(version="1.0")
        tpl2 = make_template(version="2.0")
        reg.register(tpl1)
        reg.register(tpl2)
        # latest should be 2.0
        assert reg.get("test_type") is tpl2

    def test_register_duplicate_raises(self):
        reg = PromptRegistry()
        reg.register(make_template(version="1.0"))
        with pytest.raises(ValueError, match="already registered"):
            reg.register(make_template(version="1.0"))

    def test_get_unknown_type_raises(self):
        reg = PromptRegistry()
        with pytest.raises(KeyError):
            reg.get("nonexistent_type")

    def test_get_unknown_version_raises(self):
        reg = PromptRegistry()
        reg.register(make_template(version="1.0"))
        with pytest.raises(KeyError):
            reg.get("test_type", version="9.9")

    def test_list_versions(self):
        reg = PromptRegistry()
        reg.register(make_template(version="1.0"))
        reg.register(make_template(version="2.0"))
        versions = reg.list_versions("test_type")
        assert "1.0" in versions
        assert "2.0" in versions

    def test_list_content_types(self):
        reg = PromptRegistry()
        reg.register(make_template(content_type="lesson"))
        reg.register(make_template(content_type="diagnostic_item", id="di"))
        types = reg.list_content_types()
        assert "lesson" in types
        assert "diagnostic_item" in types

    def test_default_registry_has_builtin_types(self):
        reg = PromptRegistry.default()
        types = reg.list_content_types()
        assert "diagnostic_item" in types
        assert "lesson" in types

    def test_default_registry_templates_renderable(self):
        reg = PromptRegistry.default()
        tpl = reg.get("diagnostic_item")
        rendered = tpl.render_user(
            caps_ref="4.MATH.1.1",
            grade=4,
            subject="Mathematics",
            language="en",
            source_context="Fractions are parts of a whole.",
            count=5,
        )
        assert "4.MATH.1.1" in rendered

    def test_get_prompt_registry_singleton(self):
        r1 = get_prompt_registry()
        r2 = get_prompt_registry()
        assert r1 is r2
