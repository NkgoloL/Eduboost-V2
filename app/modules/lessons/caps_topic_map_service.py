"""
app/modules/lessons/caps_topic_map_service.py
─────────────────────────────────────────────────────────────────────────────
L1-07 · Phase 1: Lesson Schema, Contract & CAPS Topic Map

CAPSTopicMapService: load the canonical CAPS topic map JSON, validate
caps_ref codes, and answer curriculum-metadata queries.

Used by:
  - lesson_validator.py (Phase 2 · L2-01): Rule 1 — caps_ref must resolve
  - lesson_generator.py (Phase 3 · L3-02): inject topic metadata into prompt
  - review coverage endpoint (Phase 4 · L4-08): list topics by grade/subject
  - tests (L1-09): valid ref passes, invalid ref rejected

Design
  - The service is intentionally synchronous: the topic map is a small static
    JSON file that loads in < 10 ms and is cached in memory for the process
    lifetime.  No async I/O is needed.
  - Multiple map files can be registered (e.g., grade4_maths.json,
    grade5_maths.json).  They are merged into one lookup at startup.

BUG FIX (L1-07): The _DEFAULT_MAP_PATHS used .parents[4] which resolved to
  the *parent* of the project root (one level too high). The correct depth
  from app/modules/lessons/ to the project root is .parents[3].
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _discover_default_map_paths() -> list[Path]:
    """Return canonical topic-map paths in stable load order.

    The launch map still lives at the legacy path. New maps should live under
    data/caps/topic_maps so Grades R-7 can be added without changing code.
    """
    paths: list[Path] = []
    topic_maps_dir = _PROJECT_ROOT / "data" / "caps" / "topic_maps"
    if topic_maps_dir.exists():
        paths.extend(sorted(topic_maps_dir.glob("*.json")))
    legacy_launch_map = _PROJECT_ROOT / "data" / "caps" / "caps_topic_map_grade4_maths.json"
    canonical_launch_map = topic_maps_dir / legacy_launch_map.name
    if legacy_launch_map.exists() and not canonical_launch_map.exists() and legacy_launch_map not in paths:
        paths.append(legacy_launch_map)
    return paths


_DEFAULT_MAP_PATHS: list[Path] = _discover_default_map_paths()


# ─── Data classes (read-only view of map entries) ─────────────────────────────


@dataclass(frozen=True)
class SubtopicEntry:
    caps_ref: str
    subtopic_index: int
    subtopic: str
    assessment_standards: list[str]
    prerequisites: list[str]
    common_misconceptions: list[str]


@dataclass(frozen=True)
class TopicEntry:
    caps_ref: str
    topic_index: int
    topic: str
    subtopics: list[SubtopicEntry]


@dataclass(frozen=True)
class TermEntry:
    term: int
    weeks: str
    topics: list[TopicEntry]


@dataclass(frozen=True)
class TopicMapMeta:
    schema_version: str
    scope: str
    source: str
    grade: int
    subject: str
    subject_code: str


@dataclass
class CAPSTopicMap:
    meta: TopicMapMeta
    terms: list[TermEntry]
    # Flat lookup: caps_ref → (TopicEntry | SubtopicEntry)
    _ref_index: dict[str, TopicEntry | SubtopicEntry] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self._build_index()

    def _build_index(self) -> None:
        for term in self.terms:
            for topic in term.topics:
                self._ref_index[topic.caps_ref] = topic
                for subtopic in topic.subtopics:
                    self._ref_index[subtopic.caps_ref] = subtopic

    def resolve(self, caps_ref: str) -> Optional[TopicEntry | SubtopicEntry]:
        """Return the entry for caps_ref, or None if it does not exist."""
        return self._ref_index.get(caps_ref)

    @property
    def all_refs(self) -> list[str]:
        return list(self._ref_index.keys())


# ─── Service ──────────────────────────────────────────────────────────────────


class CAPSTopicMapService:
    """
    Singleton-style service that loads one or more CAPS topic map JSON files
    and answers curriculum metadata queries.

    Usage (application startup)
    ───────────────────────────
        service = CAPSTopicMapService()
        service.load_maps()           # loads default paths

        # or custom paths:
        service = CAPSTopicMapService(map_paths=[Path("data/caps/grade4.json")])
        service.load_maps()

    Typical call sites
    ──────────────────
        service.validate_caps_ref("4.M.1.1")        # → True
        service.validate_caps_ref("99.X.9.9")       # → False
        service.get_topic_metadata("4.M.1.1")       # → TopicEntry
        service.list_topics(grade=4, term=1)        # → [TopicEntry, ...]
        service.get_prerequisites("4.M.1.2.2")      # → ["4.M.1.2.1"]
        service.get_misconceptions("4.M.1.1.1")     # → ["place_value_confusion", ...]
    """

    def __init__(self, map_paths: Optional[list[Path]] = None) -> None:
        self._map_paths: list[Path] = map_paths or _discover_default_map_paths()
        self._maps: list[CAPSTopicMap] = []
        self._global_index: dict[str, TopicEntry | SubtopicEntry] = {}
        self._loaded: bool = False
        self.load_maps()

    # ─── Lifecycle ────────────────────────────────────────────────────────

    def load_maps(self) -> None:
        """Load and index all configured map files. Idempotent."""
        if self._loaded:
            return
        for path in self._map_paths:
            if not path.exists():
                logger.warning("CAPS topic map not found at %s — skipping", path)
                continue
            try:
                topic_map = self._parse_map_file(path)
                self._maps.append(topic_map)
                self._global_index.update(topic_map._ref_index)
                logger.info(
                    "Loaded CAPS topic map: %s (%d refs)",
                    path.name,
                    len(topic_map._ref_index),
                )
            except Exception as exc:
                logger.error("Failed to load CAPS topic map %s: %s", path, exc)
                raise RuntimeError(f"Could not load CAPS topic map '{path}': {exc}") from exc
        self._loaded = True

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            raise RuntimeError(
                "CAPSTopicMapService.load_maps() has not been called. "
                "Call it at application startup before using the service."
            )

    # ─── Parsing ──────────────────────────────────────────────────────────

    @staticmethod
    def _parse_map_file(path: Path) -> CAPSTopicMap:
        with path.open(encoding="utf-8") as fh:
            raw = json.load(fh)

        meta_raw = raw.get("_meta", {})
        meta = TopicMapMeta(
            schema_version=meta_raw.get("schema_version", "unknown"),
            scope=meta_raw.get("scope", ""),
            source=meta_raw.get("source", ""),
            grade=raw["grade"],
            subject=raw["subject"],
            subject_code=raw["subject_code"],
        )

        terms: list[TermEntry] = []
        for term_raw in raw.get("terms", []):
            topics: list[TopicEntry] = []
            for topic_raw in term_raw.get("topics", []):
                subtopics: list[SubtopicEntry] = []
                for st_raw in topic_raw.get("subtopics", []):
                    subtopics.append(
                        SubtopicEntry(
                            caps_ref=st_raw["caps_ref"],
                            subtopic_index=st_raw["subtopic_index"],
                            subtopic=st_raw["subtopic"],
                            assessment_standards=st_raw.get("assessment_standards", []),
                            prerequisites=st_raw.get("prerequisites", []),
                            common_misconceptions=st_raw.get("common_misconceptions", []),
                        )
                    )
                topics.append(
                    TopicEntry(
                        caps_ref=topic_raw["caps_ref"],
                        topic_index=topic_raw["topic_index"],
                        topic=topic_raw["topic"],
                        subtopics=subtopics,
                    )
                )
            terms.append(
                TermEntry(
                    term=term_raw["term"],
                    weeks=term_raw.get("weeks", ""),
                    topics=topics,
                )
            )

        return CAPSTopicMap(meta=meta, terms=terms)

    # ─── Query API ────────────────────────────────────────────────────────

    def is_valid_ref(self, caps_ref: str) -> bool:
        return self.validate_caps_ref(caps_ref)

    def validate_caps_ref(self, caps_ref: str) -> bool:
        """
        Return True if caps_ref is present in the loaded topic map(s).
        This is the primary validation gate used by lesson_validator.py.
        """
        self._ensure_loaded()
        return caps_ref in self._global_index

    def get_topic_metadata(
        self, caps_ref: str
    ) -> Optional[TopicEntry | SubtopicEntry]:
        """
        Return the TopicEntry or SubtopicEntry for the given caps_ref,
        or None if not found.
        """
        self._ensure_loaded()
        return self._global_index.get(caps_ref)

    def get_assessment_standards(self, caps_ref: str) -> list[str]:
        """
        Return the assessment standards for a subtopic caps_ref.
        Returns [] for topic-level refs (which have no direct standards).
        """
        self._ensure_loaded()
        entry = self._global_index.get(caps_ref)
        if isinstance(entry, SubtopicEntry):
            return entry.assessment_standards
        return []

    def get_prerequisites(self, caps_ref: str) -> list[str]:
        """Return prerequisite caps_refs for a subtopic, or [] for topic-level refs."""
        self._ensure_loaded()
        entry = self._global_index.get(caps_ref)
        if isinstance(entry, SubtopicEntry):
            return entry.prerequisites
        return []

    def get_misconceptions(self, caps_ref: str) -> list[str]:
        """Return common misconception tags for a subtopic."""
        self._ensure_loaded()
        entry = self._global_index.get(caps_ref)
        if isinstance(entry, SubtopicEntry):
            return entry.common_misconceptions
        return []

    def get_topic_context(self, caps_ref: str) -> Optional[dict]:
        """Return a normalized generation context for any topic or subtopic ref."""
        self._ensure_loaded()
        for topic_map in self._maps:
            for term_entry in topic_map.terms:
                for topic in term_entry.topics:
                    if topic.caps_ref == caps_ref:
                        standards: list[str] = []
                        misconceptions: list[str] = []
                        prerequisites: list[str] = []
                        for subtopic in topic.subtopics:
                            standards.extend(subtopic.assessment_standards)
                            misconceptions.extend(subtopic.common_misconceptions)
                            prerequisites.extend(subtopic.prerequisites)
                        return {
                            "caps_ref": topic.caps_ref,
                            "grade": topic_map.meta.grade,
                            "subject": topic_map.meta.subject,
                            "subject_code": topic_map.meta.subject_code,
                            "term": term_entry.term,
                            "weeks": term_entry.weeks,
                            "topic": topic.topic,
                            "subtopic": topic.topic,
                            "skill": topic.topic,
                            "assessment_standards": list(dict.fromkeys(standards)),
                            "learning_outcomes": list(dict.fromkeys(standards)),
                            "prerequisites": list(dict.fromkeys(prerequisites)),
                            "common_misconceptions": list(dict.fromkeys(misconceptions)),
                        }
                    for subtopic in topic.subtopics:
                        if subtopic.caps_ref == caps_ref:
                            return {
                                "caps_ref": subtopic.caps_ref,
                                "grade": topic_map.meta.grade,
                                "subject": topic_map.meta.subject,
                                "subject_code": topic_map.meta.subject_code,
                                "term": term_entry.term,
                                "weeks": term_entry.weeks,
                                "topic": topic.topic,
                                "subtopic": subtopic.subtopic,
                                "skill": subtopic.subtopic,
                                "assessment_standards": subtopic.assessment_standards,
                                "learning_outcomes": subtopic.assessment_standards,
                                "prerequisites": subtopic.prerequisites,
                                "common_misconceptions": subtopic.common_misconceptions,
                            }
        return None

    def iter_topic_contexts(
        self,
        *,
        grade: Optional[int] = None,
        subject_code: Optional[str] = None,
        include_subtopics: bool = True,
    ) -> list[dict]:
        """Return normalized generation contexts across loaded maps."""
        contexts: list[dict] = []
        self._ensure_loaded()
        for topic_map in self._maps:
            if grade is not None and topic_map.meta.grade != grade:
                continue
            if subject_code is not None and topic_map.meta.subject_code != subject_code:
                continue
            for term_entry in topic_map.terms:
                for topic in term_entry.topics:
                    topic_context = self.get_topic_context(topic.caps_ref)
                    if topic_context:
                        contexts.append(topic_context)
                    if include_subtopics:
                        for subtopic in topic.subtopics:
                            subtopic_context = self.get_topic_context(subtopic.caps_ref)
                            if subtopic_context:
                                contexts.append(subtopic_context)
        return contexts

    def list_topics(
        self,
        grade: Optional[int] = None,
        subject_code: Optional[str] = None,
        term: Optional[int] = None,
    ) -> list[TopicEntry]:
        """
        Return TopicEntry objects matching the given filters.
        All filters are optional; omitting a filter means 'any'.
        """
        self._ensure_loaded()
        results: list[TopicEntry] = []
        for topic_map in self._maps:
            if grade is not None and topic_map.meta.grade != grade:
                continue
            if subject_code is not None and topic_map.meta.subject_code != subject_code:
                continue
            for term_entry in topic_map.terms:
                if term is not None and term_entry.term != term:
                    continue
                results.extend(term_entry.topics)
        return results

    def list_all_caps_refs(self) -> list[str]:
        """Return every caps_ref across all loaded maps."""
        self._ensure_loaded()
        return list(self._global_index.keys())

    def summary(self) -> dict:
        """Return a metadata summary for logging/health checks."""
        self._ensure_loaded()
        return {
            "maps_loaded": len(self._maps),
            "total_refs": len(self._global_index),
            "scopes": [m.meta.scope for m in self._maps],
        }


# ─── Module-level singleton for production use ───────────────────────────────
# Instantiated lazily; call load_maps() at application startup (e.g. in
# app/api_v2.py lifespan handler).

_default_service: Optional[CAPSTopicMapService] = None


def get_caps_topic_map_service() -> CAPSTopicMapService:
    return get_caps_service()


def get_caps_service() -> CAPSTopicMapService:
    """
    Return the process-wide CAPSTopicMapService singleton.
    Call load_maps() before first use.
    """
    global _default_service
    if _default_service is None:
        _default_service = CAPSTopicMapService()
    return _default_service


CapsTopicMapService = CAPSTopicMapService
