"""
CommonLit ELA Scraper
======================
Collects reading comprehension passages from CommonLit (commonlit.org).

CommonLit provides high-quality literary and informational texts
paired with comprehension questions for Grades 3–12, aligned to
Common Core ELA standards.

Content targets (CAPS English Home Language / First Additional):
  • Guided reading passages
  • Comprehension questions (literal + inferential)
  • Text complexity metadata (Lexile, grade band)

Access pattern:
  CommonLit does not provide a public API. We target the browse/library
  pages which render a filterable grid of texts. Playwright is required
  for pagination; basic aiohttp covers static pages.

Rate limit: 0.3 RPS.
License: CC BY-NC-SA 4.0.
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

_BASE       = "https://www.commonlit.org"
_LIBRARY    = f"{_BASE}/en/library"

# Grade-band landing pages that serve content lists
_GRADE_PAGES: list[dict[str, Any]] = [
    {"url": f"{_LIBRARY}?grade=3",  "grades": [3],       "subject": "english_home_language"},
    {"url": f"{_LIBRARY}?grade=4",  "grades": [4],       "subject": "english_home_language"},
    {"url": f"{_LIBRARY}?grade=5",  "grades": [5],       "subject": "english_home_language"},
    {"url": f"{_LIBRARY}?grade=6",  "grades": [6],       "subject": "english_home_language"},
    {"url": f"{_LIBRARY}?grade=7",  "grades": [7],       "subject": "english_home_language"},
    {"url": f"{_LIBRARY}?grade=8",  "grades": [8],       "subject": "english_home_language"},
    {"url": f"{_LIBRARY}?grade=9",  "grades": [9],       "subject": "english_home_language"},
    {"url": f"{_LIBRARY}?grade=10", "grades": [10],      "subject": "english_home_language"},
    {"url": f"{_LIBRARY}?grade=11", "grades": [11, 12],  "subject": "english_home_language"},
    {"url": f"{_LIBRARY}?grade=12", "grades": [11, 12],  "subject": "english_home_language"},
]

# Approximate Lexile→CAPS difficulty mapping
_LEXILE_TO_DIFFICULTY = [
    (0,   499,  "foundation"),
    (500, 799,  "developing"),
    (800, 1099, "achieved"),
    (1100, 9999, "advanced"),
]


class CommonLitScraper(BaseScraper):
    """
    Ingests CommonLit reading passages and associated questions.

    Each passage + questions → one RawContent record
    (kind=reading_passage or assessment_item).
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(config=SOURCES["commonlit"], **kwargs)

    async def scrape(self) -> AsyncIterator[RawContent]:
        pages = [
            p for p in _GRADE_PAGES
            if any(self._within_grade_range(g) for g in p["grades"])
        ]
        self._total = len(pages)
        logger.info("[CommonLit] Targeting %d grade-level library pages", self._total)

        for i, page in enumerate(pages):
            if self._at_limit():
                break
            self._emit(i, self._total, f"CommonLit Grade {page['grades']}")
            async for item in self._scrape_library_page(page):
                if self._at_limit():
                    return
                yield item

    async def _scrape_library_page(
        self, page: dict[str, Any]
    ) -> AsyncIterator[RawContent]:
        """Fetch a CommonLit library grid page and follow text links."""
        html = await self._get(page["url"])
        if not html or not isinstance(html, str):
            # Try Playwright fallback (JS pagination)
            html = await self._playwright_get(page["url"])
        if not html:
            return

        soup  = BeautifulSoup(html, "html.parser")
        links = self._extract_text_links(soup)
        logger.info("[CommonLit] Grade %s → %d text links", page["grades"], len(links))

        for link_url in links[:40]:  # cap per grade page
            if self._at_limit():
                return
            item = await self._scrape_text_page(link_url, page)
            if item:
                self._done += 1
                yield item

    @staticmethod
    def _extract_text_links(soup: BeautifulSoup) -> list[str]:
        """Extract individual text/story page URLs from a library grid."""
        links: list[str] = []
        seen: set[str]   = set()
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            # CommonLit text URLs: /en/texts/{slug}
            if "/en/texts/" in href and href not in seen:
                full = href if href.startswith("http") else f"https://www.commonlit.org{href}"
                seen.add(href)
                links.append(full)
        return links

    async def _scrape_text_page(
        self, url: str, page_meta: dict[str, Any]
    ) -> RawContent | None:
        """Fetch a single CommonLit text page and parse its content."""
        html = await self._get(url)
        if not html or not isinstance(html, str):
            html = await self._playwright_get(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # Remove UI chrome
        for tag in soup.select("nav, header, footer, script, style, [aria-hidden='true'], .ads"):
            tag.decompose()

        # ── Title ────────────────────────────────────────────────────────────
        title_el = (
            soup.select_one("h1.text-title")
            or soup.select_one(".text-header h1")
            or soup.select_one("h1")
        )
        title = title_el.get_text(strip=True) if title_el else url.split("/")[-1]

        # ── Author ───────────────────────────────────────────────────────────
        author_el = soup.select_one(".author-name, .text-author, [data-testid='author']")
        author    = author_el.get_text(strip=True) if author_el else "Unknown"

        # ── Lexile / grade metadata ───────────────────────────────────────────
        lexile    = self._extract_lexile(soup)
        difficulty = self._lexile_to_difficulty(lexile)

        # ── Reading passage ──────────────────────────────────────────────────
        passage_el = (
            soup.select_one(".text-body")
            or soup.select_one("article.text-content")
            or soup.select_one(".reading-passage")
            or soup.select_one("main article")
        )
        passage_text = ""
        if passage_el:
            passage_text = re.sub(
                r"\n{3,}", "\n\n",
                passage_el.get_text(separator="\n", strip=True)
            ).strip()

        if len(passage_text) < 100:
            return None

        # ── Comprehension questions ───────────────────────────────────────────
        questions = self._extract_questions(soup)

        grade = page_meta["grades"][0]  # Use lower bound of grade range

        return RawContent(
            source_id          = "commonlit",
            source_url         = url,
            source_internal_id = url.rstrip("/").split("/")[-1],
            raw_text           = passage_text,
            raw_html           = html,
            raw_json           = {
                "author":    author,
                "lexile":    lexile,
                "questions": questions,
            },
            metadata           = {
                "kind":       "reading_passage",
                "title":      title,
                "author":     author,
                "lexile":     lexile,
                "difficulty": difficulty,
                "subject":    page_meta["subject"],
                "grade":      grade,
                "grades":     page_meta["grades"],
                "jurisdiction": "us",
            },
            license  = "CC BY-NC-SA 4.0",
            language = "en",
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_questions(soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Parse comprehension questions from a CommonLit text page."""
        questions: list[dict[str, Any]] = []
        for q_el in soup.select(".question, .comprehension-question, [data-question-id]"):
            stem_el = q_el.select_one(".question-stem, .question-text, p:first-child")
            stem    = stem_el.get_text(strip=True) if stem_el else q_el.get_text(strip=True)[:300]
            q_type  = "open_ended"
            options: list[str] = []
            answer: str | None = None

            choice_els = q_el.select(".choice-text, .option-label, li.answer-option")
            if choice_els:
                q_type  = "mcq"
                options = [el.get_text(strip=True) for el in choice_els]
                correct = q_el.select_one(".correct-choice, [data-correct='true']")
                answer  = correct.get_text(strip=True) if correct else None

            if stem:
                questions.append({
                    "question": stem,
                    "type":     q_type,
                    "options":  options,
                    "answer":   answer,
                })
        return questions

    @staticmethod
    def _extract_lexile(soup: BeautifulSoup) -> int | None:
        """Extract Lexile score from page metadata."""
        for sel in [".lexile-score", "[data-lexile]", ".text-level"]:
            el = soup.select_one(sel)
            if el:
                text = el.get_text(strip=True)
                m    = re.search(r"(\d{3,4})", text)
                if m:
                    return int(m.group(1))
        return None

    @staticmethod
    def _lexile_to_difficulty(lexile: int | None) -> str:
        if lexile is None:
            return "achieved"
        for lo, hi, label in _LEXILE_TO_DIFFICULTY:
            if lo <= lexile <= hi:
                return label
        return "advanced"
