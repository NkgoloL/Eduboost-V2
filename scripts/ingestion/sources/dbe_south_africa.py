"""
DBE South Africa Scraper
=========================
Downloads publicly available materials from the Department of Basic Education:

  1. Mind the Gap study guides (PDF → text extraction)
  2. NSC past exam papers (Grade 10–12)
  3. CAPS curriculum statement documents

These are Crown / Government documents in the public domain.
They provide authoritative, CAPS-aligned content but require PDF parsing.
"""
from __future__ import annotations

import io
import logging
import re
from typing import Any, AsyncIterator

from scripts.ingestion.config import SOURCES
from scripts.ingestion.models import RawContent
from scripts.ingestion.sources.base import BaseScraper

logger = logging.getLogger(__name__)

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
}

# Non-language Mind the Gap subjects we prioritise for CAPS training data.
_MIND_THE_GAP_SUBJECTS = {
    "mathematics", "mathematical_literacy", "physical_sciences", "life_sciences",
    "accounting", "business_studies", "economics", "geography", "history",
    "english_home_language", "natural_sciences",
}

_PAGES_PER_RECORD = 5   # chunk large PDFs into multi-page records
# Fallback PDF links when live discovery fails (legacy paths — may 404).
_MIND_THE_GAP_FALLBACK: list[dict[str, Any]] = []

# Past NSC exam paper index pages
_PAST_PAPERS_INDEX: list[dict[str, Any]] = [
    {"url": "https://www.education.gov.za/Curriculum/NationalSeniorCertificate(NSC)Examinations/NSCPastExaminationpapers.aspx",
     "description": "NSC Past Papers Index", "grades": [10, 11, 12]},
]


class DBESouthAfricaScraper(BaseScraper):
    """
    Downloads and extracts text from DBE study guides and past papers.
    Requires `pdfplumber` for PDF extraction.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(config=SOURCES["dbe"], **kwargs)

    async def scrape(self) -> AsyncIterator[RawContent]:
        # Discover Mind the Gap PDFs dynamically from the DBE index page
        discovered: list[dict[str, Any]] = []
        try:
            discovered = await self._discover_mind_the_gap_links()
        except Exception as exc:  # pragma: no cover - best-effort discovery
            logger.warning("[DBE] Discovery failed: %s", exc)

        docs = [
            d for d in (discovered or _MIND_THE_GAP_FALLBACK)
            if self._within_grade_range(d.get("grade"))
            and d.get("subject") in _MIND_THE_GAP_SUBJECTS
        ]
        self._total = len(docs)
        logger.info("[DBE] Downloading %d Mind the Gap guides", self._total)

        for i, doc in enumerate(docs):
            if self._at_limit():
                break
            self._emit(i, self._total, f"DBE: {doc['title']}")
            async for item in self._iter_pdf_chunks(doc):
                if self._at_limit():
                    return
                self._done += 1
                yield item

        # Also scrape the NSC past papers index for paper listings
        async for item in self._scrape_past_papers():
            if self._at_limit():
                return
            yield item

    async def _iter_pdf_chunks(self, doc: dict[str, Any]) -> AsyncIterator[RawContent]:
        """Download a PDF and yield one RawContent record per page chunk."""
        try:
            import pdfplumber  # type: ignore
        except ImportError:
            logger.warning(
                "[DBE] pdfplumber not installed — skipping PDF extraction"
            )
            return

        logger.info("[DBE] Downloading: %s", doc["url"])
        pdf_bytes = await self._download_pdf(doc["url"])
        if not pdf_bytes:
            return

        pages: list[dict[str, Any]] = []
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    if len(text.strip()) > 50:
                        pages.append({"page": page_num, "text": text.strip()})
        except Exception as exc:  # noqa: BLE001
            logger.error("[DBE] PDF parse failed for %s: %s", doc["title"], exc)
            return

        if not pages:
            return

        for chunk_start in range(0, len(pages), _PAGES_PER_RECORD):
            chunk = pages[chunk_start: chunk_start + _PAGES_PER_RECORD]
            full_text = re.sub(
                r"\n{3,}", "\n\n",
                "\n\n".join(p["text"] for p in chunk),
            ).strip()
            if len(full_text) < 200:
                continue

            page_lo = chunk[0]["page"]
            page_hi = chunk[-1]["page"]
            yield RawContent(
                source_id          = "dbe",
                source_url         = doc["url"],
                source_internal_id = f"{doc['url'].split('/')[-1]}_p{page_lo}-{page_hi}",
                raw_text           = full_text,
                raw_json           = {"pages": chunk},
                metadata           = {
                    "kind":         "textbook_section",
                    "title":        f"{doc['title']} (pp. {page_lo}–{page_hi})",
                    "subject":      doc["subject"],
                    "grade":        doc["grade"],
                    "jurisdiction": "za",
                    "caps_subject": doc["subject"],
                    "doc_type":     "mind_the_gap",
                },
                license  = "Government Open License (ZA)",
                language = "en",
            )

    async def _download_pdf(self, url: str) -> bytes | None:
        """Download PDF bytes using a browser User-Agent."""
        assert self._session is not None
        from scripts.ingestion.utils.robots_checker import can_fetch
        from scripts.ingestion.utils.rate_limiter import throttle

        allowed = await can_fetch(url, self.config.robots_txt_url)
        if not allowed:
            return None
        await throttle(self.config.id, self.config.rate_limit_rps)

        try:
            async with self._session.get(url, headers=_BROWSER_HEADERS) as resp:
                if resp.status == 200:
                    return await resp.read()
                logger.warning("[DBE] HTTP %d for %s", resp.status, url)
        except Exception as exc:  # noqa: BLE001
            logger.error("[DBE] Download failed: %s", exc)
        return None

    async def _discover_mind_the_gap_links(self) -> list[dict[str, Any]]:
        """Scrape the DBE 'Mind the Gap' index page and return PDF links.

        Falls back to returning an empty list if discovery fails; the caller
        may choose to fall back to a static list.
        """
        index_url = self.config.extra.get("mind_the_gap") if self.config.extra else None
        if not index_url:
            index_url = f"{self.config.base_url}/Curriculum/LearningandTeachingSupportMaterials(LTSM)/MindtheGap.aspx"

        html = await self._get(index_url, headers=_BROWSER_HEADERS)
        if not html or not isinstance(html, str):
            logger.info("[DBE] No Mind the Gap index HTML available at %s", index_url)
            return []

        from bs4 import BeautifulSoup  # type: ignore
        from urllib.parse import urljoin

        soup = BeautifulSoup(html, "html.parser")
        anchors = soup.find_all("a", href=re.compile(r"LinkClick\.aspx", re.I))
        docs: list[dict[str, Any]] = []
        seen: set[str] = set()

        for a in anchors:
            href = a.get("href", "")
            text = a.get_text(strip=True) or ""
            if not href or text.lower() == "download":
                continue
            if "forcedownload" in href.lower():
                continue
            pdf_url = urljoin(self.config.base_url, href)
            if pdf_url in seen:
                continue
            seen.add(pdf_url)

            title   = text or pdf_url.split("/")[-1]
            subject = self._classify_mind_the_gap_subject(title, href)
            if subject not in _MIND_THE_GAP_SUBJECTS:
                continue

            docs.append({
                "url":     pdf_url,
                "title":   f"Mind the Gap {title.title()}",
                "subject": subject,
                "grade":   12,
            })

        logger.info("[DBE] Discovered %d Mind the Gap PDFs", len(docs))
        return docs

    @staticmethod
    def _classify_mind_the_gap_subject(title: str, href: str) -> str:
        t = (title + " " + href).lower()
        if "math lit" in t or "mathematical literacy" in t:
            return "mathematical_literacy"
        if "math" in t or "mathemat" in t:
            return "mathematics"
        if "physical" in t or "physics" in t:
            return "physical_sciences"
        if "life" in t or "biology" in t:
            return "life_sciences"
        if "account" in t:
            return "accounting"
        if "business" in t:
            return "business_studies"
        if "economic" in t:
            return "economics"
        if "geograph" in t:
            return "geography"
        if "history" in t:
            return "history"
        if "english" in t:
            return "english_home_language"
        return "unknown"

    async def _scrape_past_papers(self) -> AsyncIterator[RawContent]:
        """Fetch NSC past paper listing and extract PDF links."""
        for index in _PAST_PAPERS_INDEX:
            html = await self._get(index["url"], headers=_BROWSER_HEADERS)
            if not html or not isinstance(html, str):
                continue
            from bs4 import BeautifulSoup
            soup  = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", href=re.compile(r"LinkClick|\.pdf", re.I))
            logger.info("[DBE] Found %d past paper links on index page", len(links))
            for a in links[:50]:
                if self._at_limit():
                    return
                href     = a.get("href", "")
                from urllib.parse import urljoin
                pdf_url  = urljoin(self.config.base_url, href)
                text     = a.get_text(strip=True)
                meta     = self._classify_past_paper(text, pdf_url)
                if not meta or not self._within_grade_range(meta.get("grade")):
                    continue
                async for item in self._iter_pdf_chunks({
                    "url": pdf_url,
                    "title": text,
                    "grade": meta["grade"],
                    "subject": meta["subject"],
                }):
                    if self._at_limit():
                        return
                    self._done += 1
                    yield item

    @staticmethod
    def _classify_past_paper(title: str, url: str) -> dict[str, Any] | None:
        """Extract subject and grade from a paper filename/title."""
        t = title.lower()
        g = None
        for grade in range(10, 13):
            if f"grade {grade}" in t or f"gr{grade}" in t or f"gr {grade}" in t:
                g = grade
                break
        subject = "unknown"
        if "math" in t:        subject = "mathematics"
        elif "physics" in t:   subject = "physical_sciences"
        elif "biology" in t or "life" in t: subject = "life_sciences"
        elif "english" in t:   subject = "english_home_language"
        elif "history" in t:   subject = "history"
        elif "geography" in t: subject = "geography"
        elif "accounting" in t:subject = "accounting"
        elif "economics" in t: subject = "economics"
        if g and subject != "unknown":
            return {"subject": subject, "grade": g}
        return None
