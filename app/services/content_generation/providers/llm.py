"""Canonical LLM-backed Content Factory provider.

The Phase 1 provider router owns provider order, timeout, fallback and telemetry.
This adapter owns prompt construction and conversion into the Content Factory's
typed artifact contracts. It deliberately does not create a second provider
abstraction.
"""
from __future__ import annotations

import json
from typing import Any

from app.core.config import get_settings
from app.services.content_generation.prompt_payloads import (
    DiagnosticGenerationRequest,
    GeneratedDiagnosticItem,
    GeneratedLesson,
    LessonGenerationRequest,
)
from app.services.llm_provider import build_provider_router
from app.services.safety_filter import SafetyFilter


class LLMContentGenerationProvider:
    provider_name = "llm"
    model_name = "provider-router"

    def __init__(self, *, router: Any | None = None, safety_filter: SafetyFilter | None = None) -> None:
        self._router = router or build_provider_router(get_settings())
        self._safety = safety_filter or SafetyFilter()

    async def generate_diagnostic_items(
        self, request: DiagnosticGenerationRequest
    ) -> list[GeneratedDiagnosticItem]:
        count = max(1, request.missing_count)
        result = await self._router.generate(
            system=(
                "You are a South African CAPS curriculum specialist. Return strict JSON only. "
                "Generate grounded, age-appropriate multiple-choice diagnostic items."
            ),
            user=(
                f"Generate exactly {count} diagnostic items for Grade {request.grade} "
                f"{request.subject_code}, CAPS reference {request.caps_ref}, topic "
                f"{request.topic_title}, language {request.language}. Each item must contain "
                "question_text, options, correct_answer, explanation, difficulty and "
                "cognitive_level. Ground every item in the source text and do not include "
                "personal information. Return {\"items\": [...]} only.\n\n"
                f"SOURCE TEXT:\n{_source_context(request.source_chunks)}"
            ),
            temperature=0.3,
            max_tokens=3000,
        )
        raw_items = _json_items(result.text, key="items")
        source_ids = [chunk.source_chunk_id for chunk in request.source_chunks]
        items: list[GeneratedDiagnosticItem] = []
        for raw in raw_items[:count]:
            options = [str(value) for value in raw.get("options") or []]
            correct_answer = raw.get("correct_answer")
            if correct_answer is None and isinstance(raw.get("correct_answer_index"), int):
                index = int(raw["correct_answer_index"])
                if 0 <= index < len(options):
                    correct_answer = options[index]
            item = GeneratedDiagnosticItem(
                question_text=str(raw.get("question_text") or raw.get("question") or ""),
                options=options,
                correct_answer=str(correct_answer or ""),
                explanation=str(raw.get("explanation") or ""),
                caps_ref=request.caps_ref,
                grade=request.grade,
                subject_code=request.subject_code,
                language=request.language,
                difficulty=str(raw.get("difficulty") or raw.get("difficulty_band") or "medium"),
                cognitive_level=str(raw.get("cognitive_level") or raw.get("bloom_level") or "understand"),
                source_chunk_ids=source_ids,
            )
            _assert_safe(self._safety, item.to_artifact_json())
            items.append(item)
        if not items:
            raise ValueError("LLM provider returned no diagnostic items.")
        return items

    async def generate_lessons(
        self, request: LessonGenerationRequest
    ) -> list[GeneratedLesson]:
        count = max(1, request.missing_count)
        result = await self._router.generate(
            system=(
                "You are a South African CAPS educator. Return strict JSON only. Generate "
                "grounded, age-appropriate lessons with answer keys."
            ),
            user=(
                f"Generate exactly {count} lessons for Grade {request.grade} "
                f"{request.subject_code}, CAPS reference {request.caps_ref}, topic "
                f"{request.topic_title}, language {request.language}. Each lesson must contain "
                "title, summary, learning_objectives, teacher_notes, learner_activity, "
                "worked_examples, practice_questions and answer_key. Return "
                "{\"lessons\": [...]} only.\n\n"
                f"SOURCE TEXT:\n{_source_context(request.source_chunks)}"
            ),
            temperature=0.4,
            max_tokens=5000,
        )
        raw_lessons = _json_items(result.text, key="lessons")
        source_ids = [chunk.source_chunk_id for chunk in request.source_chunks]
        lessons: list[GeneratedLesson] = []
        for raw in raw_lessons[:count]:
            body = str(raw.get("body_markdown") or raw.get("learner_activity") or "")
            lesson = GeneratedLesson(
                title=str(raw.get("title") or request.topic_title),
                summary=str(raw.get("summary") or body[:500]),
                learning_objectives=_string_list(raw.get("learning_objectives")),
                teacher_notes=str(raw.get("teacher_notes") or ""),
                learner_activity=body,
                worked_examples=_string_list(raw.get("worked_examples")),
                practice_questions=_string_list(raw.get("practice_questions")),
                answer_key=_string_list(raw.get("answer_key")),
                caps_ref=request.caps_ref,
                grade=request.grade,
                subject_code=request.subject_code,
                language=request.language,
                source_chunk_ids=source_ids,
            )
            _assert_safe(self._safety, lesson.to_artifact_json())
            lessons.append(lesson)
        if not lessons:
            raise ValueError("LLM provider returned no lessons.")
        return lessons

    async def generate_assessment_blueprints(self, request: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError("Assessment blueprint generation is outside the Phase 1 launch scope.")

    async def generate_study_plan_templates(self, request: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError("Study-plan template generation is outside the Phase 1 launch scope.")


def _source_context(chunks: list[Any], max_chars: int = 8000) -> str:
    parts: list[str] = []
    used = 0
    for chunk in chunks:
        if str(getattr(chunk, "document_status", "")).lower() not in {
            "approved",
            "indexed",
            "training_ready",
        }:
            continue
        text = str(getattr(chunk, "text", ""))
        remaining = max_chars - used
        if remaining <= 0:
            break
        excerpt = text[:remaining]
        parts.append(f"[{getattr(chunk, 'source_chunk_id', 'source')}]\n{excerpt}")
        used += len(excerpt)
    if not parts:
        raise ValueError("LLM generation requires approved source context.")
    return "\n\n---\n\n".join(parts)


def _json_items(text: str, *, key: str) -> list[dict[str, Any]]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
        cleaned = cleaned.rsplit("```", 1)[0]
    payload = json.loads(cleaned)
    if isinstance(payload, list):
        values = payload
    elif isinstance(payload, dict):
        values = payload.get(key)
        if values is None and key == "items":
            values = payload.get("diagnostic_items")
    else:
        values = None
    if not isinstance(values, list):
        raise ValueError(f"LLM response must contain a JSON array under {key!r}.")
    if not all(isinstance(value, dict) for value in values):
        raise ValueError("Every generated entry must be a JSON object.")
    return values


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        return [str(value)]
    result: list[str] = []
    for item in value:
        if isinstance(item, dict):
            result.append(json.dumps(item, sort_keys=True))
        else:
            result.append(str(item))
    return result


def _assert_safe(safety: SafetyFilter, payload: dict[str, Any]) -> None:
    result = safety.check_text(json.dumps(payload, sort_keys=True), context="llm_output")
    if not result.passed:
        reasons = "; ".join(violation.description for violation in result.violations)
        raise ValueError(f"Generated content failed the safety gate: {reasons}")
