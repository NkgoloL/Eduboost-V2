"""
CK-12 Foundation Scraper
=========================
Fetches open educational content from CK-12 via their public REST API.

CK-12 publishes STEM FlexBooks and concept cards for Grades 1–12 under
CC BY-NC 3.0.  The API surface we target:

  GET /api/v1/subject/                    — subject catalogue
  GET /api/v1/browsegrid/subject/{slug}/  — grade-level topics
  GET /api/v1/flx/get/minimal/artifact/{artifact_id}  — concept body
  GET /api/v1/search/?q={term}&...        — keyword search

Content hierarchy: Subject → Branch → Concept → Reading/Practice/Video
We collect: Reading (lesson text) and Practice (exercise items).

Rate limit: 0.5 RPS (conservative — CK-12 asks for respectful crawling).
License: CC BY-NC 3.0
"""
from __future__ import annotations

import logging
import re
from typing import Any, AsyncIterator

from bs4 import BeautifulSoup

from scripts.ingestion.config import SOURCES
from scripts.ingestion.models import RawContent
from scripts.ingestion.sources.base import BaseScraper

logger = logging.getLogger(__name__)

_API_BASE    = "https://api.ck12.org/api/v1"
_SUBJECT_URL = f"{_API_BASE}/subject/"

# CK-12 subject slugs → CAPS subject / grade-range mapping
_SUBJECT_MAP: dict[str, dict[str, Any]] = {
    "math":              {"caps_subject": "mathematics",        "grades": list(range(1, 13))},
    "arithmetic":        {"caps_subject": "mathematics",        "grades": list(range(1, 7))},
    "algebra":           {"caps_subject": "mathematics",        "grades": list(range(8, 13))},
    "geometry":          {"caps_subject": "mathematics",        "grades": list(range(8, 13))},
    "statistics":        {"caps_subject": "mathematics",        "grades": list(range(10, 13))},
    "calculus":          {"caps_subject": "mathematics",        "grades": [12]},
    "biology":           {"caps_subject": "life_sciences",      "grades": list(range(10, 13))},
    "life-science":      {"caps_subject": "natural_sciences",   "grades": list(range(6, 10))},
    "chemistry":         {"caps_subject": "physical_sciences",  "grades": list(range(10, 13))},
    "physics":           {"caps_subject": "physical_sciences",  "grades": list(range(10, 13))},
    "earth-science":     {"caps_subject": "natural_sciences",   "grades": list(range(7, 10))},
    "science":           {"caps_subject": "natural_sciences",   "grades": list(range(4, 10))},
    "english":           {"caps_subject": "english_home_language", "grades": list(range(1, 13))},
    "history":           {"caps_subject": "history",            "grades": list(range(7, 13))},
    "geography":         {"caps_subject": "geography",          "grades": list(range(7, 13))},
    "economics":         {"caps_subject": "economics",          "grades": list(range(10, 13))},
}

# Maximum concepts to fetch per subject (guards against runaway crawls)
_MAX_PER_SUBJECT = 500


class CK12Scraper(BaseScraper):
    """
    Ingests CK-12 concept readings and practice items via the REST API.

    Each concept Reading → one RawContent (kind=lesson).
    Each concept Practice question → one RawContent (kind=exercise).
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(config=SOURCES["ck12"], **kwargs)

    # ── Public interface ──────────────────────────────────────────────────────

    async def scrape(self) -> AsyncIterator[RawContent]:
        subjects = await self._get(_SUBJECT_URL)
        if not isinstance(subjects, dict):
            logger.error("[CK-12] Failed to fetch subject catalogue")
            return

        subject_list: list[dict[str, Any]] = subjects.get("subjects", [])
        self._total = len(subject_list)
        logger.info("[CK-12] Found %d subjects", self._total)

        for i, subject in enumerate(subject_list):
            if self._at_limit():
                break
            slug = subject.get("handle") or subject.get("slug", "")
            caps_info = _SUBJECT_MAP.get(slug)
            if not caps_info:
                continue

            grade_lo, grade_hi = self.grade_range
            if not any(grade_lo <= g <= grade_hi for g in caps_info["grades"]):
                continue

            self._emit(i, self._total, f"CK-12 subject: {slug}")
            async for item in self._scrape_subject(subject, caps_info):
                if self._at_limit():
                    return
                yield item

    # ── Subject walker ────────────────────────────────────────────────────────

    async def _scrape_subject(
        self,
        subject: dict[str, Any],
        caps_info: dict[str, Any],
    ) -> AsyncIterator[RawContent]:
        """Walk a subject's branch → concept tree and yield content."""
        subject_id = subject.get("id") or subject.get("handle", "")
        browse_url = f"{_API_BASE}/browsegrid/subject/{subject_id}/"
        grid = await self._get(browse_url)
        if not isinstance(grid, dict):
            return

        branches: list[dict[str, Any]] = (
            grid.get("branches") or grid.get("subjects") or []
        )
        subject_count = 0

        for branch in branches:
            if self._at_limit() or subject_count >= _MAX_PER_SUBJECT:
                return
            concepts: list[dict[str, Any]] = branch.get("concepts", [])
            for concept in concepts:
                if self._at_limit() or subject_count >= _MAX_PER_SUBJECT:
                    return
                async for item in self._scrape_concept(concept, caps_info):
                    subject_count += 1
                    yield item

    # ── Concept fetcher ───────────────────────────────────────────────────────

    async def _scrape_concept(
        self,
        concept: dict[str, Any],
        caps_info: dict[str, Any],
    ) -> AsyncIterator[RawContent]:
        """Fetch the Reading and Practice artifacts for one concept."""
        concept_id    = concept.get("id") or concept.get("encodedID", "")
        concept_title = concept.get("title") or concept.get("name", concept_id)
        grade         = self._infer_grade(concept, caps_info)

        if grade is not None and not self._within_grade_range(grade):
            return

        # Reading (lesson text)
        reading = await self._fetch_artifact(concept_id, "reading")
        if reading:
            self._done += 1
            yield RawContent(
                source_id          = "ck12",
                source_url         = f"https://www.ck12.org/c/{concept_id}",
                source_internal_id = f"{concept_id}_reading",
                raw_text           = reading["text"],
                raw_html           = reading["html"],
                metadata           = {
                    "kind":         "lesson",
                    "title":        concept_title,
                    "subject":      caps_info["caps_subject"],
                    "grade":        grade,
                    "grades":       caps_info["grades"],
                    "concept_id":   concept_id,
                },
                license  = "CC BY-NC 3.0",
                language = "en",
            )

        # Practice items (exercises)
        practice = await self._fetch_artifact(concept_id, "practice")
        if practice:
            self._done += 1
            yield RawContent(
                source_id          = "ck12",
                source_url         = f"https://www.ck12.org/c/{concept_id}/practice",
                source_internal_id = f"{concept_id}_practice",
                raw_text           = practice["text"],
                raw_html           = practice["html"],
                raw_json           = practice.get("questions"),
                metadata           = {
                    "kind":       "exercise",
                    "title":      f"{concept_title} — Practice",
                    "subject":    caps_info["caps_subject"],
                    "grade":      grade,
                    "grades":     caps_info["grades"],
                    "concept_id": concept_id,
                },
                license  = "CC BY-NC 3.0",
                language = "en",
            )

    async def _fetch_artifact(
        self, concept_id: str, artifact_type: str
    ) -> dict[str, Any] | None:
        """Fetch and parse a CK-12 artifact (reading or practice)."""
        url  = f"{_API_BASE}/flx/get/minimal/artifact/{concept_id}/{artifact_type}/"
        data = await self._get(url)
        if not isinstance(data, dict):
            return None

        html = (
            data.get("artifact", {}).get("body")
            or data.get("body")
            or data.get("content", "")
        )
        if not html:
            return None

        soup  = BeautifulSoup(str(html), "html.parser")
        for tag in soup.select("script, style, nav, .feedback, .quiz-nav"):
            tag.decompose()

        plain = soup.get_text(separator="\n", strip=True)
        plain = re.sub(r"\n{3,}", "\n\n", plain).strip()
        if len(plain) < 80:
            return None

        # Extract MCQ items from practice content
        questions: list[dict[str, Any]] | None = None
        if artifact_type == "practice":
            questions = self._extract_questions(soup)

        return {"text": plain, "html": str(html), "questions": questions}

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_questions(soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Parse MCQ blocks from a CK-12 practice page."""
        questions: list[dict[str, Any]] = []
        for q_block in soup.select(".question, .practice-question, [data-question]"):
            stem_el  = q_block.select_one(".stem, .question-text, p:first-child")
            stem     = stem_el.get_text(strip=True) if stem_el else q_block.get_text(strip=True)[:200]
            choices  = [
                el.get_text(strip=True)
                for el in q_block.select(".choice, .option, li")
            ]
            correct_el = q_block.select_one(".correct, [data-correct='true']")
            correct    = correct_el.get_text(strip=True) if correct_el else None
            if stem:
                questions.append({
                    "question": stem,
                    "options":  choices,
                    "answer":   correct,
                })
        return questions

    @staticmethod
    def _infer_grade(concept: dict[str, Any], caps_info: dict[str, Any]) -> int | None:
        """Best-effort grade extraction from concept metadata."""
        for key in ("grade", "gradeLevel", "grade_level"):
            val = concept.get(key)
            if isinstance(val, int) and 1 <= val <= 12:
                return val
            if isinstance(val, str):
                m = re.search(r"(\d+)", val)
                if m:
                    g = int(m.group(1))
                    if 1 <= g <= 12:
                        return g
        # Fall back: median of declared grade range
        grades = caps_info.get("grades", [])
        return grades[len(grades) // 2] if grades else None
