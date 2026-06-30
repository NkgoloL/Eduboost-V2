"""Contract and quality validation for generated scope lesson artifacts."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

LESSON_VARIANTS = (
    "standard",
    "visual",
    "story",
    "step_by_step",
    "real_world_sa",
    "exam_style",
)

MIN_LESSON_BODY_LENGTH = 200
MIN_TEACHER_NOTES_LENGTH = 80
MIN_PARENT_NOTES_LENGTH = 60
MIN_EXTENSION_PROMPT_LENGTH = 40

PLACEHOLDER_WORKED_EXAMPLE_STEPS = (
    "start with the known facts",
    "work one step at a time",
    "write the answer clearly",
    "explain why the answer makes sense",
)

PLACEHOLDER_WORKED_EXAMPLE_ANSWERS = (
    "the final answer is checked and explained.",
    "the answer matches the important details.",
)

GENERIC_QUESTION_PATTERNS = (
    re.compile(r"^which answer shows the best idea for .+\?$", re.I),
    re.compile(r"^what should you do first\?$", re.I),
)

GENERIC_OPTION_PATTERNS = (
    re.compile(r"guess the answer before reading", re.I),
    re.compile(r"choose the same answer for every", re.I),
    re.compile(r"ignore the topic and change the order", re.I),
    re.compile(r"use the information in the .+ question carefully", re.I),
)

GENERIC_TEACHER_NOTE_PATTERNS = (
    re.compile(r"^this lesson teaches .+ in clear, short steps\.?$", re.I),
    re.compile(r"^use simple class examples with counters, drawings, examples, and discussion\.?$", re.I),
)

GENERIC_PARENT_NOTE_PATTERNS = (
    re.compile(r"^ask your child to explain .+ in their own words\.?$", re.I),
    re.compile(r"^encourage your child to read the question carefully\.?$", re.I),
)

SUBJECT_FAMILY_BY_CODE = {
    "M": "mathematics",
    "HL": "languages",
    "FAL": "languages",
    "LS": "life_skills",
    "LO": "life_orientation",
    "NST": "natural_sciences",
    "NS": "natural_sciences",
    "TECH": "technology",
    "SS": "social_sciences",
    "EMS": "social_sciences",
    "CA": "creative_arts",
    "CR": "coding_and_robotics",
}


@dataclass(frozen=True)
class GeneratedLessonQualityIssue:
    lesson_id: str
    caps_ref: str
    field: str
    reason: str


@dataclass
class GeneratedLessonQualityResult:
    passed: bool
    lesson_count: int
    failed_lesson_count: int
    issues: list[GeneratedLessonQualityIssue] = field(default_factory=list)
    aggregate: dict[str, int] = field(default_factory=dict)

    def failure_messages(self) -> list[str]:
        return [f"{issue.lesson_id}/{issue.caps_ref} {issue.field}: {issue.reason}" for issue in self.issues]


def subject_family(subject_code: str, *, subject: str | None = None) -> str:
    family = SUBJECT_FAMILY_BY_CODE.get(subject_code.upper())
    if family:
        return family
    subject_text = (subject or "").casefold()
    if "language" in subject_text:
        return "languages"
    if "life skill" in subject_text or "life orientation" in subject_text:
        return "life_skills"
    if "science" in subject_text or "technology" in subject_text:
        return "natural_sciences"
    if "social" in subject_text or "economic" in subject_text:
        return "social_sciences"
    if "creative" in subject_text or "art" in subject_text:
        return "creative_arts"
    if "coding" in subject_text or "robot" in subject_text:
        return "coding_and_robotics"
    return "mathematics"


class GeneratedLessonQualityValidator:
    """Reject placeholder/template generated lessons before staging or import."""

    def validate_lesson(
        self,
        lesson: dict[str, Any],
        *,
        scope_id: str | None = None,
        subject_code: str | None = None,
        subject: str | None = None,
        source_document_ids: list[str] | None = None,
    ) -> list[GeneratedLessonQualityIssue]:
        lesson_id = str(lesson.get("lesson_id") or "unknown")
        caps_ref = str(lesson.get("caps_ref") or "unknown")
        issues: list[GeneratedLessonQualityIssue] = []

        def add(field: str, reason: str) -> None:
            issues.append(GeneratedLessonQualityIssue(lesson_id=lesson_id, caps_ref=caps_ref, field=field, reason=reason))

        for required_field, min_len in (
            ("title", 8),
            ("scope_id", 3),
            ("variant", 3),
            ("lesson_body", MIN_LESSON_BODY_LENGTH),
            ("teacher_notes", MIN_TEACHER_NOTES_LENGTH),
            ("parent_notes", MIN_PARENT_NOTES_LENGTH),
        ):
            value = lesson.get(required_field)
            if not value or not str(value).strip():
                add(required_field, "missing or empty")
            elif min_len > 1 and len(str(value).strip()) < min_len:
                add(required_field, f"below minimum length {min_len}")

        if scope_id and lesson.get("scope_id") and str(lesson["scope_id"]) != scope_id:
            add("scope_id", f"expected {scope_id}, got {lesson['scope_id']}")

        variant = str(lesson.get("variant") or lesson.get("variant_type") or "")
        if variant and variant not in LESSON_VARIANTS:
            add("variant", f"unsupported variant {variant!r}")

        extension_prompts = lesson.get("extension_prompts") or []
        if not extension_prompts:
            add("extension_prompts", "missing or empty")
        elif any(len(str(prompt).strip()) < MIN_EXTENSION_PROMPT_LENGTH for prompt in extension_prompts):
            add("extension_prompts", "one or more prompts are too short")

        citations = lesson.get("source_citations") or []
        if not citations:
            add("source_citations", "missing source linkage")
        elif source_document_ids:
            cited_ids = {str(row.get("source_document_id") or row.get("document_id") or "") for row in citations}
            if not cited_ids.intersection(set(source_document_ids)):
                add("source_citations", "citations do not trace to scope source documents")

        objectives = lesson.get("learning_objectives") or []
        if not objectives:
            add("learning_objectives", "missing")
        elif all(str(item).casefold().startswith("work with ") for item in objectives):
            add("learning_objectives", "objectives are generic topic restatements")

        family = subject_family(subject_code or "", subject=subject or lesson.get("subject"))
        issues.extend(self._validate_worked_examples(lesson, add))
        issues.extend(self._validate_practice_questions(lesson, add))
        issues.extend(self._validate_answer_key(lesson, add))
        issues.extend(self._validate_guidance(lesson, add))
        issues.extend(self._validate_subject_family(lesson, family, add))
        return issues

    def validate_file_payload(
        self,
        payload: dict[str, Any],
        *,
        scope_id: str,
        subject_code: str | None = None,
        subject: str | None = None,
        source_document_ids: list[str] | None = None,
    ) -> GeneratedLessonQualityResult:
        lessons = payload.get("lessons") or []
        issues: list[GeneratedLessonQualityIssue] = []
        aggregate = {
            "missing_lesson_body": 0,
            "missing_title": 0,
            "missing_scope_id": 0,
            "missing_variant": 0,
            "missing_teacher_notes": 0,
            "missing_parent_notes": 0,
            "missing_extension_prompts": 0,
            "practice_questions_correct_option_a": 0,
            "lessons_with_identical_answer_keys": 0,
            "placeholder_worked_example_steps": 0,
        }

        for lesson in lessons:
            lesson_issues = self.validate_lesson(
                lesson,
                scope_id=scope_id,
                subject_code=subject_code,
                subject=subject,
                source_document_ids=source_document_ids,
            )
            issues.extend(lesson_issues)
            if not str(lesson.get("lesson_body") or "").strip():
                aggregate["missing_lesson_body"] += 1
            if not str(lesson.get("title") or "").strip():
                aggregate["missing_title"] += 1
            if not str(lesson.get("scope_id") or "").strip():
                aggregate["missing_scope_id"] += 1
            if not str(lesson.get("variant") or lesson.get("variant_type") or "").strip():
                aggregate["missing_variant"] += 1
            if not str(lesson.get("teacher_notes") or "").strip():
                aggregate["missing_teacher_notes"] += 1
            if not str(lesson.get("parent_notes") or "").strip():
                aggregate["missing_parent_notes"] += 1
            if not lesson.get("extension_prompts"):
                aggregate["missing_extension_prompts"] += 1

            practice = lesson.get("practice_questions") or []
            if practice and all(str(q.get("correct_option") or "A") == "A" for q in practice):
                aggregate["practice_questions_correct_option_a"] += len(practice)

            answer_texts = [
                str(row.get("correct_answer_text") or row.get("correct_option") or "")
                for row in (lesson.get("answer_key") or [])
            ]
            if answer_texts and len(set(answer_texts)) == 1:
                aggregate["lessons_with_identical_answer_keys"] += 1

            for example in lesson.get("worked_examples") or []:
                steps = example.get("step_by_step_solution") or []
                joined = " ".join(str(step) for step in steps).casefold()
                if any(phrase in joined for phrase in PLACEHOLDER_WORKED_EXAMPLE_STEPS):
                    aggregate["placeholder_worked_example_steps"] += 1
                    break

        failed_lessons = len({issue.lesson_id for issue in issues})
        return GeneratedLessonQualityResult(
            passed=not issues,
            lesson_count=len(lessons),
            failed_lesson_count=failed_lessons,
            issues=issues,
            aggregate=aggregate,
        )

    def _validate_worked_examples(self, lesson: dict[str, Any], add) -> list[GeneratedLessonQualityIssue]:
        issues: list[GeneratedLessonQualityIssue] = []
        examples = lesson.get("worked_examples") or []
        if len(examples) < 2:
            add("worked_examples", "fewer than two worked examples")
            return issues

        for index, example in enumerate(examples):
            answer = str(example.get("answer") or "").strip()
            if answer.casefold() in PLACEHOLDER_WORKED_EXAMPLE_ANSWERS:
                add(f"worked_examples[{index}].answer", "placeholder answer text")
            steps = example.get("step_by_step_solution") or []
            joined = " ".join(str(step) for step in steps).casefold()
            if any(phrase in joined for phrase in PLACEHOLDER_WORKED_EXAMPLE_STEPS):
                add(f"worked_examples[{index}].step_by_step_solution", "placeholder solution steps")
        return issues

    def _validate_practice_questions(self, lesson: dict[str, Any], add) -> list[GeneratedLessonQualityIssue]:
        practice = lesson.get("practice_questions") or []
        if len(practice) < 3:
            add("practice_questions", "fewer than three practice questions")
            return []

        texts = [str(q.get("question_text") or "") for q in practice]
        if len(set(texts)) != len(texts):
            add("practice_questions", "duplicate question_text within lesson")

        for question in practice:
            text = str(question.get("question_text") or "")
            if any(pattern.match(text.strip()) for pattern in GENERIC_QUESTION_PATTERNS):
                add("practice_questions", f"generic question pattern: {text}")
                break
            options = question.get("options") or {}
            option_values = list(options.values()) if isinstance(options, dict) else []
            if option_values and all(
                any(pattern.search(str(option)) for pattern in GENERIC_OPTION_PATTERNS)
                for option in option_values[:1]
            ):
                add("practice_questions", "options use generic study-behaviour distractors")

        if practice and all(str(q.get("correct_option") or "A") == "A" for q in practice):
            add("practice_questions", "all practice questions use correct option A")
        return []

    def _validate_answer_key(self, lesson: dict[str, Any], add) -> list[GeneratedLessonQualityIssue]:
        answer_key = lesson.get("answer_key") or []
        if not answer_key:
            add("answer_key", "missing answer key")
            return []
        answer_texts = [
            str(row.get("correct_answer_text") or row.get("correct_option") or "")
            for row in answer_key
        ]
        if answer_texts and len(set(answer_texts)) == 1:
            add("answer_key", "all answer-key entries share identical answer text")
        return []

    def _validate_guidance(self, lesson: dict[str, Any], add) -> list[GeneratedLessonQualityIssue]:
        teacher_notes = str(lesson.get("teacher_notes") or "").strip()
        parent_notes = str(lesson.get("parent_notes") or "").strip()
        explanation = str(lesson.get("explanation") or lesson.get("lesson_body") or "").strip()

        if teacher_notes and (
            teacher_notes == explanation
            or any(pattern.match(teacher_notes) for pattern in GENERIC_TEACHER_NOTE_PATTERNS)
        ):
            add("teacher_notes", "generic or duplicated teacher guidance")

        if parent_notes and (
            parent_notes == explanation
            or any(pattern.match(parent_notes) for pattern in GENERIC_PARENT_NOTE_PATTERNS)
        ):
            add("parent_notes", "generic or duplicated parent guidance")
        return []

    def _validate_subject_family(self, lesson: dict[str, Any], family: str, add) -> list[GeneratedLessonQualityIssue]:
        body = " ".join(
            [
                str(lesson.get("lesson_body") or ""),
                str(lesson.get("explanation") or ""),
                " ".join(str(item) for item in (lesson.get("learning_objectives") or [])),
            ]
        ).casefold()
        topic = str(lesson.get("topic") or lesson.get("subtopic") or "").casefold()
        if topic and topic not in body:
            add("lesson_body", "lesson body does not reference the scope topic")

        concrete_markers = {
            "mathematics": re.compile(r"\b\d[\d\s,]*\b"),
            "languages": re.compile(r"\b(read|write|spell|sentence|paragraph|passage|verb|noun)\b", re.I),
            "natural_sciences": re.compile(r"\b(experiment|observe|measure|energy|material|process|circuit)\b", re.I),
            "social_sciences": re.compile(r"\b(map|community|history|place|source|evidence|timeline)\b", re.I),
            "life_skills": re.compile(r"\b(health|feelings|choices|respect|community|responsibility)\b", re.I),
            "life_orientation": re.compile(
                r"\b(health|development|relationships|choices|responsibility|wellbeing)\b", re.I
            ),
            "technology": re.compile(r"\b(design|material|process|tool|structure|technology|build)\b", re.I),
            "creative_arts": re.compile(r"\b(draw|design|perform|create|colour|pattern|art)\b", re.I),
            "coding_and_robotics": re.compile(r"\b(code|algorithm|sequence|robot|input|output|debug)\b", re.I),
        }
        marker = concrete_markers.get(family, concrete_markers["mathematics"])
        if not marker.search(body):
            add("lesson_body", f"missing concrete {family.replace('_', ' ')} example content")
        return []
