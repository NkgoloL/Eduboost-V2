"""
EduBoost SA — Phase 2 (L2-06)
Prompt-Template Version Registry

Every LLM call records ``prompt_template_version`` in the lesson record.
Once set, the version is immutable: you cannot update a lesson's
prompt_template_version after it has been persisted.

This module provides:
  • PromptTemplateRegistry — loads, hashes, and returns versioned templates
  • validate_version_immutable() — guards against post-persist version changes

Version scheme:  <name>_v<N>  e.g. "lesson_generation_v1"
"""

from __future__ import annotations

import hashlib
import logging
import os
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path("app/modules/lessons/prompts")


class PromptTemplateRegistry:
    """Loads and versions Jinja2 prompt templates.

    Templates are identified by their logical name (e.g.
    ``lesson_generation_v1``) which must match the filename
    ``<name>.jinja2`` in PROMPTS_DIR.

    The registry computes a SHA-256 content hash on first load.
    If the file changes on disk between calls (e.g. hotfix), the hash
    changes and a warning is logged so CI can detect drift.
    """

    def __init__(self, prompts_dir: str | Path = PROMPTS_DIR) -> None:
        self._dir = Path(prompts_dir)
        self._cache: dict[str, tuple[str, str]] = {}  # name → (rendered_src, sha256)
        self._jinja = Environment(
            loader=FileSystemLoader(str(self._dir)),
            autoescape=select_autoescape(disabled_extensions=("jinja2",)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def get_template_version(self, template_name: str) -> str:
        """Return the logical version string for *template_name*.

        By convention this is the template file name without the ``.jinja2``
        suffix, e.g. ``lesson_generation_v1``.
        """
        return template_name  # name IS the version

    def get_content_hash(self, template_name: str) -> str:
        """Return a SHA-256 hex digest of the raw template source."""
        path = self._dir / f"{template_name}.jinja2"
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")
        source = path.read_text(encoding="utf-8")
        digest = hashlib.sha256(source.encode()).hexdigest()

        cached_src, cached_hash = self._cache.get(template_name, ("", ""))
        if cached_src and cached_src != source:
            logger.warning(
                "Prompt template '%s' has changed on disk! "
                "Old hash=%s, new hash=%s. Rebuild the lesson regression suite.",
                template_name,
                cached_hash[:12],
                digest[:12],
            )
        self._cache[template_name] = (source, digest)
        return digest

    def render(self, template_name: str, **context: Any) -> str:
        """Render template *template_name* with the given *context* variables."""
        template = self._jinja.get_template(f"{template_name}.jinja2")
        return template.render(**context)

    def list_templates(self) -> list[str]:
        """Return all available template names (without .jinja2 extension)."""
        return [
            p.stem
            for p in sorted(self._dir.glob("*.jinja2"))
            if not p.name.startswith("_")
        ]


def validate_version_immutable(
    existing_version: str | None,
    new_version: str,
    lesson_id: str,
) -> None:
    """Raise ValueError if a persisted lesson's prompt_template_version would change.

    Once a lesson has been persisted with a specific prompt_template_version,
    that field is immutable.  This prevents silent retroactive attribution.
    """
    if existing_version and existing_version != new_version:
        raise ValueError(
            f"Lesson '{lesson_id}' already has prompt_template_version="
            f"'{existing_version}'. Cannot overwrite with '{new_version}'. "
            "Create a new lesson instead of modifying the versioning of an "
            "existing one."
        )
