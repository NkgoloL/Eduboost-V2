"""Grounded tutor response controls for Phase 2R Gate 2R.7."""
from __future__ import annotations

from dataclasses import dataclass, field


class TutorGroundingError(ValueError):
    pass


@dataclass(frozen=True)
class TutorGroundingTrace:
    retrieval_query: str
    source_chunk_ids: list[str]
    published_artifact_ids: list[str]
    curriculum_node_ids: list[str]
    corpus_version: str | None
    grounding_status: str
    fallback_reason: str | None = None
    safety_metadata: dict = field(default_factory=dict)


class TutorGroundingPolicy:
    def validate(self, trace: TutorGroundingTrace) -> None:
        if not trace.retrieval_query.strip():
            raise TutorGroundingError("tutor retrieval_query is required")
        if trace.grounding_status == "passed":
            if not trace.corpus_version:
                raise TutorGroundingError("grounded tutor response requires corpus_version")
            if not trace.source_chunk_ids and not trace.published_artifact_ids:
                raise TutorGroundingError("grounded tutor response requires source chunks or published artifacts")
            return
        if trace.grounding_status in {"failed", "fallback"}:
            if not trace.fallback_reason:
                raise TutorGroundingError("ungrounded tutor response requires explicit safe fallback_reason")
            return
        raise TutorGroundingError(f"invalid grounding_status: {trace.grounding_status}")
