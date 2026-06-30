"""
EduBoost Phase 1 — Content Validator
======================================
Validates raw LLM text output against the typed content schemas.
Invalid or structurally incorrect output is rejected and cannot enter
the review pipeline (EC-02).

Validation contract:
  1. Strip markdown code fences if present (LLMs frequently add them).
  2. Parse JSON.  Malformed JSON → ValidationResult(passed=False).
  3. Dispatch to the correct Pydantic schema class.
  4. Return a typed ValidationResult with structured errors.
  5. Store a ContentValidationReport in the database when called with a session.

A batch diagnostic-item response is a JSON array; a lesson response is a JSON object.
"""
from __future__ import annotations

import json
import structlog
import re
from dataclasses import dataclass, field
from typing import Any

from pydantic import ValidationError

from app.services.content_schemas import (
    CONTENT_TYPE_SCHEMAS,
    DiagnosticItemBatch,
    DiagnosticItemPayload,
    LessonPayload,
    get_schema_version,
)

log = structlog.get_logger(__name__)

_FENCE_RE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", re.DOTALL | re.IGNORECASE)


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    content_type: str
    schema_version: str
    errors: list[str] = field(default_factory=list)
    validated_payload: Any = field(default=None)  # Pydantic model instance when passed

    @property
    def error_summary(self) -> str:
        return "; ".join(self.errors) if self.errors else ""


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


class ContentValidator:
    """
    Validate raw LLM output for a given content type.
    Thread-safe; stateless — construct once and reuse.
    """

    def validate(
        self,
        raw_output: str,
        content_type: str,
        *,
        caps_ref: str | None = None,
    ) -> ValidationResult:
        """
        Parse and validate *raw_output* against the schema for *content_type*.

        Returns a :class:`ValidationResult` — never raises.
        """
        schema_version = "unknown"
        try:
            schema_version = get_schema_version(content_type)
        except KeyError:
            return ValidationResult(
                passed=False,
                content_type=content_type,
                schema_version=schema_version,
                errors=[f"Unknown content type: {content_type!r}"],
            )

        stripped = self._strip_fences(raw_output)

        try:
            raw_json = json.loads(stripped)
        except json.JSONDecodeError as exc:
            log.warning(
                "validation_json_parse_failed",
                content_type=content_type,
                error=str(exc),
            )
            return ValidationResult(
                passed=False,
                content_type=content_type,
                schema_version=schema_version,
                errors=[f"JSON parse error: {exc}"],
            )

        return self._dispatch(content_type, schema_version, raw_json, caps_ref)

    # ------------------------------------------------------------------ #

    def _dispatch(
        self,
        content_type: str,
        schema_version: str,
        raw_json: Any,
        caps_ref: str | None,
    ) -> ValidationResult:
        try:
            if content_type == "diagnostic_item":
                return self._validate_diagnostic_batch(schema_version, raw_json, caps_ref)
            elif content_type == "lesson":
                return self._validate_lesson(schema_version, raw_json, caps_ref)
            else:
                schema_cls = CONTENT_TYPE_SCHEMAS.get(content_type)
                if schema_cls is None:
                    return ValidationResult(
                        passed=False,
                        content_type=content_type,
                        schema_version=schema_version,
                        errors=[f"No validator for content type {content_type!r}"],
                    )
                instance = schema_cls.model_validate(raw_json)
                return ValidationResult(
                    passed=True,
                    content_type=content_type,
                    schema_version=schema_version,
                    validated_payload=instance,
                )
        except ValidationError as exc:
            errors = [
                f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}"
                for e in exc.errors()
            ]
            log.info(
                "validation_schema_failed",
                content_type=content_type,
                error_count=len(errors),
            )
            return ValidationResult(
                passed=False,
                content_type=content_type,
                schema_version=schema_version,
                errors=errors,
            )

    def _validate_diagnostic_batch(
        self,
        schema_version: str,
        raw_json: Any,
        caps_ref: str | None,
    ) -> ValidationResult:
        # The LLM returns a JSON array of items
        if not isinstance(raw_json, list):
            return ValidationResult(
                passed=False,
                content_type="diagnostic_item",
                schema_version=schema_version,
                errors=["Expected a JSON array for diagnostic_item batch"],
            )
        if len(raw_json) == 0:
            # LLM explicitly returned empty — treat as content-policy refusal
            return ValidationResult(
                passed=False,
                content_type="diagnostic_item",
                schema_version=schema_version,
                errors=["LLM returned empty array — generation refused or no content"],
            )
        items: list[DiagnosticItemPayload] = []
        errors: list[str] = []
        for idx, raw_item in enumerate(raw_json):
            try:
                item = DiagnosticItemPayload.model_validate(raw_item)
                # Optionally enforce caps_ref consistency
                if caps_ref and item.caps_ref != caps_ref:
                    errors.append(
                        f"item[{idx}].caps_ref {item.caps_ref!r} "
                        f"does not match expected {caps_ref!r}"
                    )
                else:
                    items.append(item)
            except ValidationError as exc:
                for e in exc.errors():
                    loc = ".".join(str(x) for x in e["loc"])
                    errors.append(f"item[{idx}].{loc}: {e['msg']}")

        if errors:
            return ValidationResult(
                passed=False,
                content_type="diagnostic_item",
                schema_version=schema_version,
                errors=errors,
            )
        batch = DiagnosticItemBatch(items=items)
        return ValidationResult(
            passed=True,
            content_type="diagnostic_item",
            schema_version=schema_version,
            validated_payload=batch,
        )

    def _validate_lesson(
        self,
        schema_version: str,
        raw_json: Any,
        caps_ref: str | None,
    ) -> ValidationResult:
        if raw_json is None:
            return ValidationResult(
                passed=False,
                content_type="lesson",
                schema_version=schema_version,
                errors=["LLM returned null — generation refused"],
            )
        if not isinstance(raw_json, dict):
            return ValidationResult(
                passed=False,
                content_type="lesson",
                schema_version=schema_version,
                errors=[f"Expected JSON object for lesson, got {type(raw_json).__name__}"],
            )
        try:
            lesson = LessonPayload.model_validate(raw_json)
        except ValidationError as exc:
            errors = [
                f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}"
                for e in exc.errors()
            ]
            return ValidationResult(
                passed=False,
                content_type="lesson",
                schema_version=schema_version,
                errors=errors,
            )
        if caps_ref and lesson.caps_ref != caps_ref:
            return ValidationResult(
                passed=False,
                content_type="lesson",
                schema_version=schema_version,
                errors=[
                    f"lesson.caps_ref {lesson.caps_ref!r} "
                    f"does not match expected {caps_ref!r}"
                ],
            )
        return ValidationResult(
            passed=True,
            content_type="lesson",
            schema_version=schema_version,
            validated_payload=lesson,
        )

    # ------------------------------------------------------------------ #

    @staticmethod
    def _strip_fences(text: str) -> str:
        """Remove markdown code fences that LLMs sometimes add."""
        stripped = text.strip()
        match = _FENCE_RE.match(stripped)
        if match:
            return match.group(1).strip()
        return stripped
