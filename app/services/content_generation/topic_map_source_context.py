"""Build grounded source context payloads for scope lesson generation."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MIN_CONTEXT_TEXT_LENGTH = 120


@dataclass(frozen=True)
class TopicMapSourceContext:
    scope_id: str
    caps_ref: str
    grade: int
    phase: str | None
    subject: str
    subject_code: str
    language: str
    topic: str
    subtopic: str
    term: int
    weeks: str | None
    assessment_standards: tuple[str, ...]
    learning_outcomes: tuple[str, ...]
    prerequisites: tuple[str, ...]
    common_misconceptions: tuple[str, ...]
    vocabulary: tuple[str, ...]
    source_document_ids: tuple[str, ...]
    source_text_snippets: tuple[str, ...]
    context_hash: str

    @property
    def passed(self) -> bool:
        return bool(self.assessment_standards) and bool(self.source_document_ids) and bool(self.source_text_snippets)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope_id": self.scope_id,
            "caps_ref": self.caps_ref,
            "grade": self.grade,
            "phase": self.phase,
            "subject": self.subject,
            "subject_code": self.subject_code,
            "language": self.language,
            "topic": self.topic,
            "subtopic": self.subtopic,
            "term": self.term,
            "weeks": self.weeks,
            "assessment_standards": list(self.assessment_standards),
            "learning_outcomes": list(self.learning_outcomes),
            "prerequisites": list(self.prerequisites),
            "common_misconceptions": list(self.common_misconceptions),
            "vocabulary": list(self.vocabulary),
            "source_document_ids": list(self.source_document_ids),
            "source_text_snippets": list(self.source_text_snippets),
            "context_hash": self.context_hash,
        }


@dataclass(frozen=True)
class TopicMapSourceContextResult:
    passed: bool
    errors: list[str]
    context: TopicMapSourceContext | None = None


class TopicMapSourceContextBuilder:
    """Build deterministic source-context payloads from topic maps and scope metadata."""

    def __init__(self, *, project_root: Path) -> None:
        self.project_root = project_root

    def build(
        self,
        *,
        scope_id: str,
        caps_ref: str,
        topic_context: dict[str, Any],
        topic_map_path: str,
        source_document_ids: list[str],
        phase: str | None = None,
        language: str = "en",
    ) -> TopicMapSourceContextResult:
        errors: list[str] = []
        topic_map = _load_topic_map(self.project_root / topic_map_path)
        meta = topic_map.get("_meta") or {}

        standards = tuple(topic_context.get("assessment_standards") or topic_context.get("learning_outcomes") or ())
        if not standards:
            errors.append(f"{caps_ref}: topic map context lacks assessment standards.")

        document_ids = tuple(source_document_ids or meta.get("source_document_ids") or ())
        if not document_ids:
            errors.append(f"{caps_ref}: scope/topic map lacks source document ids.")

        snippets = self._extract_snippets(topic_map, topic_context, caps_ref)
        if not snippets:
            errors.append(f"{caps_ref}: no source text snippets available for lesson generation.")
        elif sum(len(snippet) for snippet in snippets) < MIN_CONTEXT_TEXT_LENGTH:
            errors.append(f"{caps_ref}: source context is too thin for grounded generation.")

        vocabulary = _extract_vocabulary(topic_context, snippets)
        context_payload = {
            "scope_id": scope_id,
            "caps_ref": caps_ref,
            "grade": topic_context.get("grade"),
            "phase": phase,
            "subject": topic_context.get("subject"),
            "subject_code": topic_context.get("subject_code"),
            "language": language,
            "topic": topic_context.get("topic"),
            "subtopic": topic_context.get("subtopic"),
            "term": topic_context.get("term"),
            "weeks": topic_context.get("weeks"),
            "assessment_standards": standards,
            "learning_outcomes": tuple(topic_context.get("learning_outcomes") or standards),
            "prerequisites": tuple(topic_context.get("prerequisites") or ()),
            "common_misconceptions": tuple(topic_context.get("common_misconceptions") or ()),
            "vocabulary": vocabulary,
            "source_document_ids": document_ids,
            "source_text_snippets": snippets,
        }
        context_hash = "sha256:" + hashlib.sha256(
            json.dumps(context_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        context = TopicMapSourceContext(
            scope_id=scope_id,
            caps_ref=caps_ref,
            grade=int(topic_context.get("grade") or 0),
            phase=phase,
            subject=str(topic_context.get("subject") or ""),
            subject_code=str(topic_context.get("subject_code") or ""),
            language=language,
            topic=str(topic_context.get("topic") or ""),
            subtopic=str(topic_context.get("subtopic") or topic_context.get("topic") or ""),
            term=int(topic_context.get("term") or 1),
            weeks=topic_context.get("weeks"),
            assessment_standards=standards,
            learning_outcomes=tuple(topic_context.get("learning_outcomes") or standards),
            prerequisites=tuple(topic_context.get("prerequisites") or ()),
            common_misconceptions=tuple(topic_context.get("common_misconceptions") or ("needs_step_by_step_support",)),
            vocabulary=vocabulary,
            source_document_ids=document_ids,
            source_text_snippets=snippets,
            context_hash=context_hash,
        )
        return TopicMapSourceContextResult(passed=not errors, errors=errors, context=context)

    def _extract_snippets(
        self,
        topic_map: dict[str, Any],
        topic_context: dict[str, Any],
        caps_ref: str,
    ) -> tuple[str, ...]:
        snippets: list[str] = []
        meta = topic_map.get("_meta") or {}
        for path in meta.get("source_text_extract_paths") or []:
            extract_path = self.project_root / path
            if not extract_path.exists():
                continue
            text = extract_path.read_text(encoding="utf-8", errors="ignore")
            topic_words = {
                word.casefold()
                for word in (
                    str(topic_context.get("topic") or ""),
                    str(topic_context.get("subtopic") or ""),
                    caps_ref,
                )
                if word
            }
            for paragraph in _paragraphs(text):
                lowered = paragraph.casefold()
                if any(word in lowered for word in topic_words if len(word) > 3):
                    snippets.append(paragraph.strip())
                if len(snippets) >= 3:
                    break
            if snippets:
                break

        if not snippets:
            snippets.extend(
                [
                    f"CAPS reference {caps_ref} covers {topic_context.get('subtopic') or topic_context.get('topic')}.",
                    " ".join(topic_context.get("assessment_standards") or [])[:400],
                ]
            )
        return tuple(dict.fromkeys(s for s in snippets if s.strip()))


def _load_topic_map(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _paragraphs(text: str) -> list[str]:
    chunks = [chunk.strip() for chunk in text.replace("\r", "\n").split("\n\n") if chunk.strip()]
    if chunks:
        return chunks
    return [line.strip() for line in text.splitlines() if line.strip()]


def _extract_vocabulary(topic_context: dict[str, Any], snippets: tuple[str, ...]) -> tuple[str, ...]:
    words: list[str] = []
    for key in ("topic", "subtopic", "skill"):
        value = str(topic_context.get(key) or "").strip()
        if value:
            words.extend(part for part in value.replace(",", " ").split() if len(part) > 3)
    for snippet in snippets[:2]:
        for token in snippet.split():
            cleaned = "".join(ch for ch in token if ch.isalpha())
            if len(cleaned) > 5:
                words.append(cleaned)
    return tuple(dict.fromkeys(words[:8]))
