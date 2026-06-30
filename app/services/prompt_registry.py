"""
EduBoost Phase 1 — Prompt Registry
====================================
Versioned, auditable prompt templates for CAPS-aligned content generation.
Templates are stored in code (not the database) so every change is tracked
in version control and satisfies EC-03 (prompt version attributable to every
generated artefact).

Usage::

    registry = PromptRegistry.default()
    tmpl = registry.get("diagnostic_item", "1.0")
    system_prompt = tmpl.system
    user_prompt   = tmpl.render_user(caps_ref="4.M.1.1", source_context="...", count=5)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# Template dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PromptTemplate:
    id: str                   # e.g. "diagnostic_item"
    version: str              # SemVer-like: "1.0"
    content_type: str         # aligns with ContentArtifactType enum values
    schema_version: str       # content schema version this prompt targets
    system: str               # system prompt (fixed)
    user_template: str        # user prompt with {placeholder} slots

    def render_user(self, **kwargs: Any) -> str:
        """Render the user template with provided substitutions."""
        try:
            return self.user_template.format(**kwargs)
        except KeyError as exc:
            missing = exc.args[0]
            raise ValueError(
                f"Prompt template '{self.id}' v{self.version} requires "
                f"placeholder '{{{missing}}}' but it was not provided."
            ) from exc

    @property
    def prompt_version_tag(self) -> str:
        """Canonical version tag stored in DB and evidence."""
        return f"{self.id}@{self.version}"


# ---------------------------------------------------------------------------
# Built-in CAPS-aligned templates
# ---------------------------------------------------------------------------

_DIAGNOSTIC_ITEM_SYSTEM_V1 = """\
You are an expert South African educational content author for Grade {grade} {subject}.
Your task is to write multiple-choice diagnostic items that are:
  - Strictly aligned to the South African CAPS (Curriculum and Assessment Policy Statement)
  - Age-appropriate for Grade {grade} learners
  - Factually correct with a single unambiguous correct answer
  - Free of bias, personal information, and culturally insensitive content
  - Written in clear, simple English accessible to South African learners

You MUST return a valid JSON array and nothing else — no markdown fences, no preamble, no explanation.
Each element MUST conform to this schema exactly (all fields required):

[
  {{
    "question":             "<string — the question stem, 10–300 characters>",
    "options":              ["<A>", "<B>", "<C>", "<D>"],
    "correct_answer_index": <integer 0–3>,
    "explanation":          "<string — why the correct answer is correct, 20–500 characters>",
    "bloom_level":          "<one of: knowledge|comprehension|application|analysis>",
    "difficulty_band":      "<one of: easy|medium|hard>",
    "caps_ref":             "<CAPS reference, e.g. 4.M.1.1>",
    "tags":                 ["<optional tag>"]
  }}
]

Do NOT include any personally identifiable information (names, phone numbers, ID numbers, emails).
Do NOT include violent, sexual, or disturbing content.
If you cannot generate safe, curriculum-aligned items from the provided source material, return an empty array [].
"""

_DIAGNOSTIC_ITEM_USER_V1 = """\
CAPS Reference: {caps_ref}
Grade: {grade}
Subject: {subject}
Language: {language}

SOURCE MATERIAL (use only this material to ground the items — do not invent facts):
---
{source_context}
---

Generate exactly {count} diagnostic multiple-choice item(s) for the CAPS objective above.
Each item must be clearly grounded in the source material.
Return JSON only.
"""

_LESSON_SYSTEM_V1 = """\
You are an expert South African educational content author for Grade {grade} {subject}.
Your task is to write a structured lesson aligned to the South African CAPS curriculum.
The lesson must be:
  - Factually accurate and grounded exclusively in the provided source material
  - Written in clear, accessible English for Grade {grade} learners
  - Free of personal information, bias, and culturally insensitive content
  - Structured with a clear introduction, worked examples, and summary

You MUST return a single valid JSON object and nothing else — no markdown fences, no preamble.
The object MUST conform to this schema exactly:

{{
  "title":               "<string — concise lesson title, 10–120 characters>",
  "caps_ref":            "<CAPS reference, e.g. 4.M.1.1>",
  "grade":               <integer>,
  "subject_code":        "<string, e.g. MATHS>",
  "language":            "<ISO-639-1 code, e.g. en>",
  "learning_objectives": ["<objective 1>", "<objective 2>"],
  "key_vocabulary":      [{{"term": "<word>", "definition": "<definition>"}}],
  "body_markdown":       "<markdown body — introduction, explanation, examples, summary>",
  "worked_examples": [
    {{
      "problem":   "<problem statement>",
      "solution":  "<step-by-step solution>",
      "answer":    "<final answer>"
    }}
  ]
}}

Do NOT include any personally identifiable information.
Do NOT include violent, sexual, or disturbing content.
If you cannot produce a safe, curriculum-aligned lesson from the source material, return null.
"""

_LESSON_USER_V1 = """\
CAPS Reference: {caps_ref}
Grade: {grade}
Subject: {subject}
Language: {language}

SOURCE MATERIAL (base the lesson exclusively on this — do not invent facts):
---
{source_context}
---

Write one complete lesson for the CAPS objective above.
Return JSON only.
"""


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class PromptRegistry:
    """
    Registry of versioned prompt templates keyed by (content_type, version).
    Call ``PromptRegistry.default()`` to get the singleton with all built-in
    templates registered.
    """

    def __init__(self) -> None:
        self._templates: dict[tuple[str, str], PromptTemplate] = {}
        self._latest: dict[str, str] = {}  # content_type → latest version

    def register(self, template: PromptTemplate) -> None:
        key = (template.content_type, template.version)
        if key in self._templates:
            raise ValueError(
                f"Template {template.content_type}@{template.version} "
                "is already registered.  Bump the version to make changes."
            )
        self._templates[key] = template
        # Update latest: use lexicographic comparison (SemVer without pre-release)
        current_latest = self._latest.get(template.content_type)
        if current_latest is None or template.version > current_latest:
            self._latest[template.content_type] = template.version

    def get(self, content_type: str, version: str | None = None) -> PromptTemplate:
        """
        Return the template for *content_type*.
        If *version* is None, returns the latest registered version.
        Raises KeyError if not found.
        """
        if version is None:
            version = self._latest.get(content_type)
            if version is None:
                raise KeyError(
                    f"No prompt template registered for content type '{content_type}'"
                )
        key = (content_type, version)
        if key not in self._templates:
            raise KeyError(
                f"No prompt template for {content_type}@{version}. "
                f"Available: {self.list_versions(content_type)}"
            )
        return self._templates[key]

    def list_versions(self, content_type: str) -> list[str]:
        return sorted(
            v for (ct, v) in self._templates if ct == content_type
        )

    def list_content_types(self) -> list[str]:
        return sorted({ct for (ct, _) in self._templates})

    @classmethod
    def default(cls) -> "PromptRegistry":
        """Return a registry populated with all built-in templates."""
        registry = cls()
        registry.register(
            PromptTemplate(
                id="diagnostic_item",
                version="1.0",
                content_type="diagnostic_item",
                schema_version="1.0",
                system=_DIAGNOSTIC_ITEM_SYSTEM_V1,
                user_template=_DIAGNOSTIC_ITEM_USER_V1,
            )
        )
        registry.register(
            PromptTemplate(
                id="lesson",
                version="1.0",
                content_type="lesson",
                schema_version="1.0",
                system=_LESSON_SYSTEM_V1,
                user_template=_LESSON_USER_V1,
            )
        )
        return registry


# Module-level singleton
_DEFAULT_REGISTRY: PromptRegistry | None = None


def get_prompt_registry() -> PromptRegistry:
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        _DEFAULT_REGISTRY = PromptRegistry.default()
    return _DEFAULT_REGISTRY
