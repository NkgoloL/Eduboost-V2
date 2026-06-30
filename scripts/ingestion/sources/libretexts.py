"""
LibreTexts Scraper
==================
Fetches open-access college / advanced-senior content from LibreTexts.

LibreTexts provides CC BY 4.0 licensed textbooks covering:
  Mathematics, Sciences (Physics, Chemistry, Biology), Social Sciences

For EduBoost SA, we target content suitable for FET Phase (Grades 10–12),
focusing on sections that reinforce CAPS topics without being pitched at
university level.

LibreTexts API: https://api.libretexts.org (Mindtouch REST)
Content paths:  https://{shelf}.libretexts.org/{book}/{page}

Shelves of interest:
  - math.libretexts.org
  - phys.libretexts.org
  - chem.libretexts.org
  - bio.libretexts.org
  - stats.libretexts.org

Rate limit: 0.5 RPS.
License: CC BY 4.0.
"""
from __future__ import annotations

import logging
import re
from typing import Any, AsyncIterator
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from scripts.ingestion.config import SOURCES
from scripts.ingestion.models import RawContent
from scripts.ingestion.sources.base import BaseScraper

logger = logging.getLogger(__name__)

# Books to scrape: (url, subject, grades, title)
_TARGET_BOOKS: list[dict[str, Any]] = [
    # Mathematics
    {
        "url":     "https://math.libretexts.org/Bookshelves/Algebra/Elementary_Algebra_(Ellis_and_Burzynski)",
        "subject": "mathematics", "grades": [8, 9, 10], "shelf": "math",
    },
    {
        "url":     "https://math.libretexts.org/Bookshelves/Algebra/Advanced_Algebra",
        "subject": "mathematics", "grades": [10, 11], "shelf": "math",
    },
    {
        "url":     "https://math.libretexts.org/Bookshelves/Calculus",
        "subject": "mathematics", "grades": [12], "shelf": "math",
    },
    {
        "url":     "https://stats.libretexts.org/Bookshelves/Introductory_Statistics",
        "subject": "mathematics", "grades": [10, 11, 12], "shelf": "stats",
    },
    # Physical Sciences
    {
        "url":     "https://phys.libretexts.org/Bookshelves/University_Physics/Book%3A_Physics_(Boundless)",
        "subject": "physical_sciences", "grades": [10, 11, 12], "shelf": "phys",
    },
    {
        "url":     "https://chem.libretexts.org/Bookshelves/General_Chemistry",
        "subject": "physical_sciences", "grades": [10, 11, 12], "shelf": "chem",
    },
    # Life Sciences
    {
        "url":     "https://bio.libretexts.org/Bookshelves/Introductory_and_General_Biology",
        "subject": "life_sciences", "grades": [10, 11, 12], "shelf": "bio",
    },
]

_MIN_SECTION_CHARS = 200
_MAX_SECTIONS_PER_BOOK = 80


class LibreTextsScraper(BaseScraper):
    """
    Walks LibreTexts book tables of contents and scrapes section pages.
    Each section (page) → one RawContent record.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(config=SOURCES["libretexts"], **kwargs)

    async def scrape(self) -> AsyncIterator[RawContent]:
        books = [
            b for b in _TARGET_BOOKS
            if any(self._within_grade_range(g) for g in b["grades"])
        ]
        self._total = len(books)
        logger.info("[LibreTexts] Scraping %d target books", self._total)

        for i, book in enumerate(books):
            if self._at_limit():
                break
            self._emit(i, self._total, f"LibreTexts {book['shelf']} {book['subject']}")
            async for item in self._scrape_book(book):
                if self._at_limit():
                    return
                yield item

    async def _scrape_book(self, book: dict[str, Any]) -> AsyncIterator[RawContent]:
        """Fetch a book index, extract section links, scrape each section."""
        html = await self._get(book["url"])
        if not html or not isinstance(html, str):
            logger.warning("[LibreTexts] Could not load book: %s", book["url"])
            return

        soup         = BeautifulSoup(html, "html.parser")
        section_urls = self._extract_section_links(soup, book["url"])
        logger.info("[LibreTexts] Book %s → %d sections",
                    book["url"].split("/")[-1], len(section_urls))

        count = 0
        for section_url in section_urls:
            if self._at_limit() or count >= _MAX_SECTIONS_PER_BOOK:
                return
            item = await self._scrape_section(section_url, book)
            if item:
                self._done += 1
                count += 1
                yield item

    @staticmethod
    def _extract_section_links(soup: BeautifulSoup, base_url: str) -> list[str]:
        """Extract page/section links from a LibreTexts book ToC."""
        seen:  set[str]  = set()
        links: list[str] = []
        base_domain = urlparse(base_url).netloc

        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if not href:
                continue
            full = urljoin(base_url, href)
            parsed = urlparse(full)
            # Only same-shelf links, skip anchors and external
            if (
                parsed.netloc == base_domain
                and "#" not in full
                and full not in seen
                and full != base_url
                # Skip pure index/front-matter pages
                and not any(seg in full for seg in ["Front_Matter", "Back_Matter",
                                                     "Index", "Glossary"])
            ):
                seen.add(full)
                links.append(full)
        return links

    async def _scrape_section(
        self, url: str, book: dict[str, Any]
    ) -> RawContent | None:
        """Fetch and parse a single LibreTexts section page."""
        html = await self._get(url)
        if not html or not isinstance(html, str):
            return None

        soup = BeautifulSoup(html, "html.parser")

        # Remove LibreTexts chrome
        for tag in soup.select(
            "nav, header, footer, script, style, "
            ".sidebar, #sidebar, .toc, .feedback-widget, "
            ".libretexts-login, .page-nav"
        ):
            tag.decompose()

        # Title
        title_el = soup.select_one("h1.title, h1#page-title, h1")
        title    = title_el.get_text(strip=True) if title_el else url.split("/")[-1]

        # Main content
        content_el = (
            soup.select_one("#content, .content, main article, article.lt-content")
            or soup.select_one("main")
        )
        if not content_el:
            return None

        plain = re.sub(
            r"\n{3,}", "\n\n",
            content_el.get_text(separator="\n", strip=True)
        ).strip()

        if len(plain) < _MIN_SECTION_CHARS:
            return None

        # Extract any embedded exercises/examples
        examples: list[str] = []
        for ex in content_el.select(".example, .exercise, [data-type='example']"):
            text = ex.get_text(separator="\n", strip=True)
            if len(text) > 30:
                examples.append(text)

        grade = book["grades"][len(book["grades"]) // 2]  # median grade

        return RawContent(
            source_id          = "libretexts",
            source_url         = url,
            source_internal_id = urlparse(url).path.replace("/", "_").strip("_"),
            raw_text           = plain,
            raw_html           = html,
            raw_json           = {"examples": examples, "shelf": book["shelf"]},
            metadata           = {
                "kind":     "textbook_section",
                "title":    title,
                "subject":  book["subject"],
                "grade":    grade,
                "grades":   book["grades"],
                "shelf":    book["shelf"],
            },
            license  = "CC BY 4.0",
            language = "en",
        )
