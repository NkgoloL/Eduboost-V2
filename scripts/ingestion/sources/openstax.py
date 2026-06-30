"""
OpenStax Scraper
================
Fetches Grade 6–12 textbooks from OpenStax via the CMS books API and Rex
webview pages.

License: CC BY 4.0 — all content freely redistributable with attribution.
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

_BOOKS_URL = "https://openstax.org/apps/cms/api/books/"

# Map OpenStax book slugs (without the ``books/`` prefix) to CAPS metadata.
_BOOK_CAPS_MAP: dict[str, dict[str, Any]] = {
    "prealgebra-2e":                 {"subject": "mathematics",       "grades": [7, 8, 9]},
    "elementary-algebra-2e":         {"subject": "mathematics",       "grades": [8, 9, 10]},
    "intermediate-algebra-2e":       {"subject": "mathematics",       "grades": [10, 11]},
    "algebra-and-trigonometry-2e":   {"subject": "mathematics",       "grades": [11, 12]},
    "precalculus-2e":                {"subject": "mathematics",       "grades": [11, 12]},
    "calculus-volume-1":             {"subject": "mathematics",       "grades": [12]},
    "calculus-volume-2":             {"subject": "mathematics",       "grades": [12]},
    "statistics":                    {"subject": "mathematics",       "grades": [10, 11, 12]},
    "biology-2e":                    {"subject": "life_sciences",     "grades": [10, 11, 12]},
    "microbiology":                  {"subject": "life_sciences",     "grades": [11, 12]},
    "anatomy-and-physiology":        {"subject": "life_sciences",     "grades": [11, 12]},
    "chemistry-2e":                  {"subject": "physical_sciences", "grades": [10, 11, 12]},
    "chemistry-atoms-first-2e":      {"subject": "physical_sciences", "grades": [10, 11, 12]},
    "university-physics-volume-1":   {"subject": "physical_sciences", "grades": [11, 12]},
    "university-physics-volume-2":   {"subject": "physical_sciences", "grades": [12]},
    "college-physics-2e":            {"subject": "physical_sciences", "grades": [10, 11, 12]},
    "astronomy-2e":                  {"subject": "natural_sciences",  "grades": [10, 11]},
    "earth-science":                 {"subject": "natural_sciences",  "grades": [9, 10]},
    "us-history":                    {"subject": "history",           "grades": [9, 10, 11]},
    "world-history-volume-1":        {"subject": "history",           "grades": [9, 10]},
    "world-history-volume-2":        {"subject": "history",           "grades": [10, 11]},
    "principles-economics-3e":       {"subject": "economics",         "grades": [11, 12]},
    "principles-microeconomics-3e":  {"subject": "economics",         "grades": [11, 12]},
    "principles-macroeconomics-3e":  {"subject": "economics",         "grades": [11, 12]},
    "writing-guide-with-handbook":   {"subject": "english_home_language", "grades": [10, 11, 12]},
}

_SLUG_IN_HTML_RE = re.compile(r'"slug"\s*:\s*"([a-z0-9][a-z0-9-]*)"')
_PAGE_PATH_RE    = re.compile(r"/books/([a-z0-9-]+)/pages/([a-z0-9][a-z0-9-]*)")


class OpenStaxScraper(BaseScraper):
    """Ingests OpenStax textbook content section by section."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(config=SOURCES["openstax"], **kwargs)
        self._page_slugs_cache: dict[str, list[str]] = {}

    async def scrape(self) -> AsyncIterator[RawContent]:
        data = await self._get(_BOOKS_URL)
        if not isinstance(data, dict):
            logger.error("[OpenStax] Failed to fetch book list")
            return

        book_list = data.get("books", [])
        self._total = len(book_list)
        logger.info("[OpenStax] Found %d books", self._total)

        grade_lo, grade_hi = self.grade_range
        for i, book_meta in enumerate(book_list):
            if self._at_limit():
                break

            raw_slug = book_meta.get("slug", "")
            slug     = _normalize_slug(raw_slug)
            caps_info = _BOOK_CAPS_MAP.get(slug)
            if not caps_info:
                continue

            book_grades = caps_info["grades"]
            if not any(grade_lo <= g <= grade_hi for g in book_grades):
                continue

            self._emit(i, self._total, f"Book: {slug}")
            async for item in self._scrape_book(slug, book_meta.get("title", slug), caps_info):
                if self._at_limit():
                    return
                yield item

    async def _scrape_book(
        self,
        slug: str,
        title: str,
        caps_info: dict[str, Any],
    ) -> AsyncIterator[RawContent]:
        page_slugs = await self._discover_page_slugs(slug)
        if not page_slugs:
            logger.warning("[OpenStax] No pages discovered for %s", slug)
            return

        logger.info("[OpenStax] Book %s — %d pages", title, len(page_slugs))
        for page_slug in page_slugs:
            if self._at_limit():
                return
            item = await self._fetch_page(slug, page_slug, title, caps_info)
            if item:
                self._done += 1
                yield item

    async def _discover_page_slugs(self, book_slug: str) -> list[str]:
        if book_slug in self._page_slugs_cache:
            return self._page_slugs_cache[book_slug]

        seed = f"https://openstax.org/books/{book_slug}/pages/1-introduction"
        html = await self._get(seed)
        if not html or not isinstance(html, str):
            return []

        slugs: set[str] = set(_SLUG_IN_HTML_RE.findall(html))
        for book, slug in _PAGE_PATH_RE.findall(html):
            if book == book_slug:
                slugs.add(slug)

        slugs.discard("")
        ordered = sorted(slugs)
        self._page_slugs_cache[book_slug] = ordered
        return ordered

    async def _fetch_page(
        self,
        book_slug: str,
        page_slug: str,
        book_title: str,
        caps_info: dict[str, Any],
    ) -> RawContent | None:
        url  = f"https://openstax.org/books/{book_slug}/pages/{page_slug}"
        html = await self._get(url)
        if not html or not isinstance(html, str):
            return None

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.select("nav, .toc, .sidebar, script, style, header, footer"):
            tag.decompose()

        main = soup.select_one("main") or soup.select_one("article") or soup
        plain = re.sub(r"\n{3,}", "\n\n", main.get_text(separator="\n", strip=True)).strip()
        if len(plain) < 100:
            return None

        title = page_slug.replace("-", " ").title()
        heading = main.select_one("h1, h2")
        if heading:
            title = heading.get_text(strip=True)[:250]

        return RawContent(
            source_id          = "openstax",
            source_url         = url,
            source_internal_id = f"{book_slug}/{page_slug}",
            raw_text           = plain,
            raw_html           = str(main),
            metadata           = {
                "kind":      "textbook_section",
                "book":      book_title,
                "title":     title,
                "subject":   caps_info["subject"],
                "grades":    caps_info["grades"],
            },
            license  = "CC BY 4.0",
            language = "en",
        )


def _normalize_slug(raw_slug: str) -> str:
    """``books/biology-2e`` → ``biology-2e``."""
    return raw_slug.removeprefix("books/").strip("/")
