"""
BBC Bitesize Scraper
=====================
Scrapes educational content from BBC Bitesize (www.bbc.co.uk/bitesize).

BBC Bitesize is a JS-rendered site — Playwright is required.
It organises content by Key Stage (KS1–KS4) which maps to SA Grades:

  KS1 (age 5–7)   → Foundation Phase Grades 1–2
  KS2 (age 7–11)  → Foundation/Intermediate Phase Grades 2–5
  KS3 (age 11–14) → Senior Phase Grades 6–9
  KS4 / GCSE      → FET Phase Grades 10–12

The crawl strategy:
  1. Fetch subject index: /bitesize/{level}/{subject}
  2. Discover topic links from the nav/grid
  3. For each topic page: extract lesson text, key points, and quiz items

Rate limit: 0.3 RPS — BBC's CDN is rate-sensitive.
License: BBC Educational (Non-Commercial).  Do NOT redistribute raw HTML.
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

_BASE = "https://www.bbc.co.uk/bitesize"

# (bitesize_level, subject_slug) → CAPS metadata
_ENTRY_POINTS: list[dict[str, Any]] = [
    # KS3 (Senior Phase: Grades 6–9)
    {"url": f"{_BASE}/subjects/z826n39",  "subject": "mathematics",       "grades": [6,7,8,9],   "level": "ks3"},
    {"url": f"{_BASE}/subjects/zng4d2p",  "subject": "natural_sciences",  "grades": [6,7,8,9],   "level": "ks3"},
    {"url": f"{_BASE}/subjects/zh3yyrd",  "subject": "history",           "grades": [7,8,9],     "level": "ks3"},
    {"url": f"{_BASE}/subjects/zcbchv4",  "subject": "geography",         "grades": [7,8,9],     "level": "ks3"},
    {"url": f"{_BASE}/subjects/z4hgwmn",  "subject": "english_home_language", "grades": [6,7,8,9], "level": "ks3"},
    # KS4 / GCSE (FET Phase: Grades 10–12)
    {"url": f"{_BASE}/subjects/z38pycw",  "subject": "mathematics",       "grades": [10,11,12],  "level": "ks4"},
    {"url": f"{_BASE}/subjects/zrkp34j",  "subject": "physical_sciences", "grades": [10,11,12],  "level": "ks4"},
    {"url": f"{_BASE}/subjects/z9ddmp3",  "subject": "life_sciences",     "grades": [10,11,12],  "level": "ks4"},
    {"url": f"{_BASE}/subjects/zgkw2hv",  "subject": "history",           "grades": [10,11],     "level": "ks4"},
    {"url": f"{_BASE}/subjects/zxg87ty",  "subject": "geography",         "grades": [10,11],     "level": "ks4"},
    {"url": f"{_BASE}/subjects/zr9p34j",  "subject": "economics",         "grades": [10,11,12],  "level": "ks4"},
]

# UK GCSE grade → CAPS approximate mapping
_UK_GCSE_TO_CAPS_GRADE = {
    "foundation": 10,
    "higher":     11,
    "ks3":         8,
    "ks4":        11,
}


class BBCBitesizeScraper(BaseScraper):
    """
    Playwright-based scraper for BBC Bitesize.

    Discovers topic links from subject index pages, then scrapes
    each topic for key-point summaries and quiz questions.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(config=SOURCES["bbc_bitesize"], **kwargs)

    async def scrape(self) -> AsyncIterator[RawContent]:
        # Filter entry points by requested grade range
        entries = [
            ep for ep in _ENTRY_POINTS
            if any(self._within_grade_range(g) for g in ep["grades"])
        ]
        self._total = len(entries)
        logger.info("[BBCBitesize] Scraping %d subject entry points (Playwright)", self._total)

        for i, entry in enumerate(entries):
            if self._at_limit():
                break
            self._emit(i, self._total, f"BBC Bitesize {entry['level']} {entry['subject']}")
            async for item in self._scrape_subject(entry):
                if self._at_limit():
                    return
                yield item

    async def _scrape_subject(self, entry: dict[str, Any]) -> AsyncIterator[RawContent]:
        html = await self._playwright_get(entry["url"])
        if not html:
            logger.warning("[BBCBitesize] Could not load: %s", entry["url"])
            return

        soup       = BeautifulSoup(html, "html.parser")
        topic_urls = self._extract_topic_links(soup, entry["url"])
        logger.info("[BBCBitesize] %s → %d topic links", entry["subject"], len(topic_urls))

        for topic_url in topic_urls[:60]:  # cap per subject
            if self._at_limit():
                return
            item = await self._scrape_topic(topic_url, entry)
            if item:
                self._done += 1
                yield item

    @staticmethod
    def _extract_topic_links(soup: BeautifulSoup, base_url: str) -> list[str]:
        """Pull topic/guide URLs from a Bitesize subject index page."""
        from urllib.parse import urljoin
        seen: set[str] = set()
        links: list[str] = []
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if not href:
                continue
            full = urljoin(base_url, href)
            # Only follow internal guide / topic / article links
            if (
                "bbc.co.uk/bitesize" in full
                and any(seg in full for seg in ["/guides/", "/topics/", "/articles/"])
                and "#" not in full
                and full not in seen
            ):
                seen.add(full)
                links.append(full)
        return links

    async def _scrape_topic(
        self, url: str, entry: dict[str, Any]
    ) -> RawContent | None:
        """Fetch a single Bitesize topic page and extract structured content."""
        html = await self._playwright_get(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # Remove chrome elements
        for tag in soup.select("nav, header, footer, script, style, [aria-hidden='true']"):
            tag.decompose()

        # Page title
        title_el = soup.select_one("h1")
        title    = title_el.get_text(strip=True) if title_el else url.split("/")[-1]

        # Key facts / bullet summaries (typical Bitesize structure)
        key_points: list[str] = []
        for el in soup.select(".key-points li, .summary li, .fact li, [data-testid='key-point']"):
            text = el.get_text(strip=True)
            if text:
                key_points.append(text)

        # Quiz items embedded on the page
        quiz_items: list[dict[str, Any]] = self._extract_quiz_items(soup)

        # Main body text
        main = soup.select_one("main, article, [role='main'], .gel-layout__item")
        plain = (main or soup).get_text(separator="\n", strip=True)
        plain = re.sub(r"\n{3,}", "\n\n", plain).strip()

        if len(plain) < 80:
            return None

        # Approximate CAPS grade: use median of declared range
        grades = entry["grades"]
        grade  = grades[len(grades) // 2]

        return RawContent(
            source_id          = "bbc_bitesize",
            source_url         = url,
            source_internal_id = url.split("/")[-1],
            raw_text           = plain,
            raw_html           = html,
            raw_json           = {
                "key_points": key_points,
                "quiz_items": quiz_items,
                "level":      entry["level"],
            },
            metadata           = {
                "kind":         "lesson",
                "title":        title,
                "subject":      entry["subject"],
                "grade":        grade,
                "grades":       grades,
                "jurisdiction": "uk",
            },
            license  = "BBC Educational (Non-Commercial)",
            language = "en",
        )

    @staticmethod
    def _extract_quiz_items(soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Extract embedded quiz questions from a Bitesize page."""
        items: list[dict[str, Any]] = []
        # Bitesize quiz DOM varies — try multiple selectors
        for q_block in soup.select(
            ".quiz-question, [data-testid='quiz-question'], "
            ".question-block, .bitesize-question"
        ):
            q_el = q_block.select_one(".question-text, p:first-child, h3")
            q    = q_el.get_text(strip=True) if q_el else ""
            opts = [
                el.get_text(strip=True)
                for el in q_block.select(".option, .answer-option, li")
            ]
            correct_el = q_block.select_one(".correct-answer, [data-correct]")
            correct    = correct_el.get_text(strip=True) if correct_el else None
            if q:
                items.append({"question": q, "options": opts, "answer": correct})
        return items
