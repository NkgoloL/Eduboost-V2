"""
Siyavula Open Textbooks Scraper
================================
Siyavula publishes free, CC BY 4.0 CAPS-aligned textbooks for
Grade 7–12 Mathematics and Physical Sciences.

These are the highest-value SA-specific training source because:
  • Already CAPS-aligned — minimal mapping work needed
  • Grade 7–12 coverage for Maths and Science
  • High-quality, reviewed content
  • Open license

Access pattern: HTML chapter pages structured as:
  /read/{subject}/grade-{N} → chapter list → section HTML
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

# All available Siyavula books with their CAPS metadata
_SIYAVULA_BOOKS: list[dict[str, Any]] = [
    # Mathematics
    {"url": "https://www.siyavula.com/read/maths/grade-7",  "subject": "mathematics", "grade": 7,  "caps_subject": "mathematics"},
    {"url": "https://www.siyavula.com/read/maths/grade-8",  "subject": "mathematics", "grade": 8,  "caps_subject": "mathematics"},
    {"url": "https://www.siyavula.com/read/maths/grade-9",  "subject": "mathematics", "grade": 9,  "caps_subject": "mathematics"},
    {"url": "https://www.siyavula.com/read/maths/grade-10", "subject": "mathematics", "grade": 10, "caps_subject": "mathematics"},
    {"url": "https://www.siyavula.com/read/maths/grade-11", "subject": "mathematics", "grade": 11, "caps_subject": "mathematics"},
    {"url": "https://www.siyavula.com/read/maths/grade-12", "subject": "mathematics", "grade": 12, "caps_subject": "mathematics"},
    # Physical Sciences
    {"url": "https://www.siyavula.com/read/science/grade-10", "subject": "physical_sciences", "grade": 10, "caps_subject": "physical_sciences"},
    {"url": "https://www.siyavula.com/read/science/grade-11", "subject": "physical_sciences", "grade": 11, "caps_subject": "physical_sciences"},
    {"url": "https://www.siyavula.com/read/science/grade-12", "subject": "physical_sciences", "grade": 12, "caps_subject": "physical_sciences"},
]


class SiyavulaScraper(BaseScraper):
    """
    Scrapes Siyavula open textbook sections.
    Each section (worked examples + exercises + explanations) → one record.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(config=SOURCES["siyavula"], **kwargs)

    async def scrape(self) -> AsyncIterator[RawContent]:
        books = [b for b in _SIYAVULA_BOOKS
                 if self._within_grade_range(b["grade"])]
        self._total = len(books)

        for i, book in enumerate(books):
            if self._at_limit():
                break
            self._emit(i, self._total,
                       f"Siyavula {book['subject']} Grade {book['grade']}")
            async for item in self._scrape_book(book):
                if self._at_limit():
                    return
                yield item

    async def _scrape_book(self, book: dict[str, Any]) -> AsyncIterator[RawContent]:
        html = await self._get(book["url"])
        pw_network = []
        if not html or not isinstance(html, str):
            # Siyavula may require browser rendering; capture network XHRs
            html, pw_network = await self._playwright_capture(book["url"])  # type: ignore[attr-defined]
        if not html:
            logger.warning("[Siyavula] Could not fetch: %s", book["url"])
            return

        soup    = BeautifulSoup(html, "html.parser")
        # Extract chapter/section links from the sidebar/ToC
        toc_links = self._extract_toc_links(soup, book["url"])
        # If the initial fetch returned the skeleton SPA HTML, re-render
        # with Playwright and try again (Siyavula uses client-side rendering).
        if not toc_links:
            logger.debug("[Siyavula] No TOC links found from HTTP fetch; trying Playwright render")
            pw_html, pw_network = await self._playwright_capture(book["url"])  # type: ignore[attr-defined]
            if pw_html and isinstance(pw_html, str):
                soup = BeautifulSoup(pw_html, "html.parser")
                toc_links = self._extract_toc_links(soup, book["url"])
                logger.info("[Siyavula] Playwright render — %d sections found for %s Grade %d",
                            len(toc_links), book["subject"], book["grade"])
            # Log captured XHR/fetch responses for debugging (debug-level)
            if pw_network:
                for r in pw_network:
                    body = r.get("body")
                    snippet = None
                    if body and isinstance(body, str):
                        snippet = body[:1000]
                    logger.debug("[Siyavula][Playwright XHR] %s %s status=%s snippet=%s",
                                 r.get("resource_type"), r.get("url"), r.get("status"), snippet)
        else:
            logger.info("[Siyavula] Grade %d %s — %d sections found",
                        book["grade"], book["subject"], len(toc_links))

        for link_url, section_title in toc_links:
            if self._at_limit():
                return
            item = await self._scrape_section(link_url, section_title, book)
            if item:
                self._done += 1
                yield item

    @staticmethod
    def _extract_toc_links(soup: BeautifulSoup, base_url: str) -> list[tuple[str, str]]:
        """Extract chapter and section URLs for the current Siyavula book."""
        from urllib.parse import urljoin, urlparse

        canonical = soup.select_one('link[rel="canonical"][href]')
        book_url = urljoin(base_url, canonical.get("href")) if canonical else base_url
        parsed_book = urlparse(book_url)
        book_prefix = f"{parsed_book.scheme}://{parsed_book.netloc}{parsed_book.path}".rstrip("/")

        links: list[tuple[str, str]] = []
        candidates = soup.select("main a[href], article a[href], .chapter-title[href], a.chapter-title[href]")
        for el in candidates:
            href = el.get("href") or ""
            text = el.get_text(strip=True) or ""
            if not href or not text or "#" in href:
                continue
            full_url = urljoin(book_prefix + "/", href)
            if not full_url.startswith(book_prefix + "/"):
                continue
            if "/dashboard/" in full_url or "/set-preferences/" in full_url:
                continue
            links.append((full_url, text))

        seen: set[str] = set()
        unique: list[tuple[str, str]] = []
        for u, t in links:
            if u not in seen:
                seen.add(u)
                unique.append((u, t))
        return unique

    async def _scrape_section(
        self, url: str, title: str, book: dict[str, Any]
    ) -> RawContent | None:
        html = await self._get(url)
        if not html or not isinstance(html, str):
            html = await self._playwright_get(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # Remove nav/sidebar/footer
        for tag in soup.select("nav, .sidebar, footer, script, style, .solutions-toggle"):
            tag.decompose()

        # Main content area
        main = (
            soup.select_one("main")
            or soup.select_one("article")
            or soup.select_one(".content-area")
            or soup
        )

        # Extract worked examples as separate records (valuable training data)
        worked_examples: list[dict[str, Any]] = []
        for we in main.select(".worked-example, .example, .worked_example"):
            q = we.select_one(".question, .problem")
            a = we.select_one(".solution, .answer")
            if q:
                worked_examples.append({
                    "question":  q.get_text(separator="\n", strip=True),
                    "solution":  a.get_text(separator="\n", strip=True) if a else "",
                })

        # Extract exercises (without answers — good MCQ seed material)
        exercises: list[str] = []
        for ex in main.select(".exercise, .activity, .problem"):
            text = ex.get_text(separator="\n", strip=True)
            if len(text) > 20:
                exercises.append(text)

        plain = main.get_text(separator="\n", strip=True)
        plain = re.sub(r"\n{3,}", "\n\n", plain).strip()

        if len(plain) < 100:
            return None

        # Try to infer CAPS chapter code from URL or heading
        caps_code = self._infer_caps_code(url, soup)

        return RawContent(
            source_id          = "siyavula",
            source_url         = url,
            source_internal_id = url.split("/")[-1],
            raw_text           = plain,
            raw_html           = str(main),
            raw_json           = {
                "worked_examples": worked_examples,
                "exercises":       exercises,
            },
            metadata           = {
                "kind":         "textbook_section",
                "title":        title,
                "subject":      book["subject"],
                "caps_subject": book["caps_subject"],
                "grade":        book["grade"],
                "caps_code":    caps_code,
                "jurisdiction": "za",
            },
            license    = "CC BY 4.0",
            language   = "en",
        )

    @staticmethod
    def _infer_caps_code(url: str, soup: BeautifulSoup) -> str | None:
        """Try to extract a CAPS-style topic code from URL fragments or headings."""
        # e.g. .../grade-10/chapter-2-functions → "F" (FET Functions)
        heading = soup.select_one("h1, h2")
        if heading:
            text = heading.get_text(strip=True).lower()
            if "function" in text:      return "F"
            if "trigonometr" in text:   return "T"
            if "calculus" in text:      return "DC"
            if "statistic" in text:     return "ST"
            if "probabilit" in text:    return "P"
            if "geometry" in text:      return "EG"
            if "analytic" in text:      return "AG"
            if "finance" in text:       return "FGD"
            if "sequence" in text:      return "NPS"
            if "algebra" in text:       return "A"
            if "mechanics" in text:     return "M"
            if "wave" in text:          return "W"
            if "electricit" in text:    return "EC"
            if "chemical" in text:      return "CH"
        return None
