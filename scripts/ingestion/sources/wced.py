"""
WCED (Western Cape Education Department) Scraper
=================================================
Scrapes educational materials published by the Western Cape Education
Department at wcedonline.wced.school.za.

WCED publishes CAPS-aligned resources for Grades 1–12 including:
  • e-Learning resources (structured HTML lessons)
  • Study guides per subject and grade
  • Revision packs with exercises
  • Examination guidelines

These are publicly accessible Government educational materials.
License: Government Open License (ZA) — non-commercial redistribution
is permitted with attribution.

Content hierarchy:
  Subject landing → Grade index → Resource pages → Downloadable assets

Rate limit: 0.2 RPS — government infrastructure; be conservative.
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

_BASE = "https://wcedonline.wced.school.za"

# WCED subject portals and their CAPS metadata
_SUBJECT_PORTALS: list[dict[str, Any]] = [
    {"url": f"{_BASE}/subjects/mathematics",         "subject": "mathematics",       "grades": list(range(4, 13))},
    {"url": f"{_BASE}/subjects/mathematicalliteracy","subject": "mathematical_literacy","grades": list(range(10, 13))},
    {"url": f"{_BASE}/subjects/english",             "subject": "english_home_language","grades": list(range(4, 13))},
    {"url": f"{_BASE}/subjects/afrikaans",           "subject": "afrikaans_home_language","grades": list(range(4, 13))},
    {"url": f"{_BASE}/subjects/naturalsciences",     "subject": "natural_sciences",  "grades": list(range(4, 10))},
    {"url": f"{_BASE}/subjects/lifesciences",        "subject": "life_sciences",     "grades": list(range(10, 13))},
    {"url": f"{_BASE}/subjects/physicalsciences",    "subject": "physical_sciences", "grades": list(range(10, 13))},
    {"url": f"{_BASE}/subjects/history",             "subject": "history",           "grades": list(range(7, 13))},
    {"url": f"{_BASE}/subjects/geography",           "subject": "geography",         "grades": list(range(7, 13))},
    {"url": f"{_BASE}/subjects/economics",           "subject": "economics",         "grades": list(range(10, 13))},
    {"url": f"{_BASE}/subjects/accounting",          "subject": "accounting",        "grades": list(range(10, 13))},
    {"url": f"{_BASE}/subjects/businessstudies",     "subject": "business_studies",  "grades": list(range(10, 13))},
    {"url": f"{_BASE}/subjects/technology",          "subject": "technology",        "grades": list(range(7, 10))},
    {"url": f"{_BASE}/subjects/lifeorientation",     "subject": "life_orientation",  "grades": list(range(4, 13))},
]

_GRADE_RE      = re.compile(r"\bgrade\s*(\d{1,2})\b", re.IGNORECASE)
_MAX_RESOURCES = 50  # per subject portal


class WCEDScraper(BaseScraper):
    """
    Crawls WCED subject portals for CAPS-aligned lesson and revision content.
    Handles both HTML lesson pages and PDF study guides (via pdfplumber).
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(config=SOURCES["wced"], **kwargs)

    async def scrape(self) -> AsyncIterator[RawContent]:
        portals = [
            p for p in _SUBJECT_PORTALS
            if any(self._within_grade_range(g) for g in p["grades"])
        ]
        self._total = len(portals)
        logger.info("[WCED] Scraping %d subject portals", self._total)

        for i, portal in enumerate(portals):
            if self._at_limit():
                break
            self._emit(i, self._total, f"WCED {portal['subject']}")
            async for item in self._scrape_portal(portal):
                if self._at_limit():
                    return
                yield item

    async def _scrape_portal(self, portal: dict[str, Any]) -> AsyncIterator[RawContent]:
        html = await self._get(portal["url"])
        if not html or not isinstance(html, str):
            logger.warning("[WCED] Cannot load portal: %s", portal["url"])
            return

        soup           = BeautifulSoup(html, "html.parser")
        resource_links = self._extract_resource_links(soup, portal["url"])
        logger.info("[WCED] %s — %d resource links found",
                    portal["subject"], len(resource_links))

        count = 0
        for res_url, res_title in resource_links:
            if self._at_limit() or count >= _MAX_RESOURCES:
                return
            grade = self._infer_grade_from_title(res_title, portal)
            if grade and not self._within_grade_range(grade):
                continue

            if res_url.lower().endswith(".pdf"):
                item = await self._fetch_pdf_resource(res_url, res_title, portal, grade)
            else:
                item = await self._fetch_html_resource(res_url, res_title, portal, grade)

            if item:
                self._done += 1
                count += 1
                yield item

    @staticmethod
    def _extract_resource_links(
        soup: BeautifulSoup, base_url: str
    ) -> list[tuple[str, str]]:
        """Extract (url, title) tuples for resource pages from a portal index."""
        seen:  set[str]             = set()
        links: list[tuple[str, str]] = []
        base_domain = urlparse(base_url).netloc

        for a in soup.select("a[href]"):
            href  = a.get("href", "")
            title = a.get_text(strip=True) or ""
            if not href or not title:
                continue
            full   = urljoin(base_url, href)
            parsed = urlparse(full)
            if (
                parsed.netloc == base_domain
                and full not in seen
                and len(title) > 3
            ):
                seen.add(full)
                links.append((full, title))
        return links

    async def _fetch_html_resource(
        self, url: str, title: str, portal: dict[str, Any], grade: int | None
    ) -> RawContent | None:
        html = await self._get(url)
        if not html or not isinstance(html, str):
            return None

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.select("nav, header, footer, script, style, .breadcrumb"):
            tag.decompose()

        main = (
            soup.select_one("main, article, #content, .content-area")
            or soup
        )
        plain = re.sub(r"\n{3,}", "\n\n",
                       main.get_text(separator="\n", strip=True)).strip()
        if len(plain) < 100:
            return None

        if not grade:
            grade = portal["grades"][len(portal["grades"]) // 2]

        return RawContent(
            source_id          = "wced",
            source_url         = url,
            source_internal_id = urlparse(url).path.replace("/", "_").strip("_"),
            raw_text           = plain,
            raw_html           = html,
            metadata           = {
                "kind":         "lesson",
                "title":        title,
                "subject":      portal["subject"],
                "grade":        grade,
                "grades":       portal["grades"],
                "jurisdiction": "za",
                "caps_subject": portal["subject"],
            },
            license  = "Government Open License (ZA)",
            language = "en",
        )

    async def _fetch_pdf_resource(
        self, url: str, title: str, portal: dict[str, Any], grade: int | None
    ) -> RawContent | None:
        """Download a WCED PDF study guide and extract text via pdfplumber."""
        try:
            import pdfplumber  # type: ignore
            import io
        except ImportError:
            logger.warning("[WCED] pdfplumber not installed — skipping PDF: %s", url)
            return None

        assert self._session is not None
        try:
            async with self._session.get(url) as resp:
                if resp.status != 200:
                    return None
                pdf_bytes = await resp.read()
        except Exception as exc:
            logger.error("[WCED] PDF download failed: %s", exc)
            return None

        pages: list[dict[str, Any]] = []
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    if len(text.strip()) > 50:
                        pages.append({"page": page_num, "text": text.strip()})
        except Exception as exc:
            logger.error("[WCED] PDF parse failed for %s: %s", title, exc)
            return None

        full_text = re.sub(r"\n{3,}", "\n\n",
                           "\n\n".join(p["text"] for p in pages)).strip()
        if len(full_text) < 200:
            return None

        if not grade:
            grade = portal["grades"][len(portal["grades"]) // 2]

        return RawContent(
            source_id          = "wced",
            source_url         = url,
            source_internal_id = url.split("/")[-1],
            raw_text           = full_text,
            raw_json           = {"pages": pages},
            metadata           = {
                "kind":         "textbook_section",
                "title":        title,
                "subject":      portal["subject"],
                "grade":        grade,
                "grades":       portal["grades"],
                "jurisdiction": "za",
                "caps_subject": portal["subject"],
                "doc_type":     "wced_study_guide",
            },
            license  = "Government Open License (ZA)",
            language = "en",
        )

    @staticmethod
    def _infer_grade_from_title(title: str, portal: dict[str, Any]) -> int | None:
        m = _GRADE_RE.search(title)
        if m:
            g = int(m.group(1))
            return g if 1 <= g <= 12 else None
        return None
