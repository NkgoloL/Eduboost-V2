"""
EduBoost SA — Scraper Registry
================================
Central registry that maps every source_id to its BaseScraper subclass.
Import from here rather than from individual modules to keep coupling low.

Usage::

    from scripts.ingestion.sources import SCRAPER_REGISTRY, get_scraper

    scraper = get_scraper("khan_academy", grade_range=(7, 12), limit=500)
    async with scraper:
        async for item in scraper.scrape():
            process(item)
"""
from __future__ import annotations

from typing import Any

from scripts.ingestion.sources.base import BaseScraper
from scripts.ingestion.sources.bbc_bitesize import BBCBitesizeScraper
from scripts.ingestion.sources.ck12 import CK12Scraper
from scripts.ingestion.sources.commonlit import CommonLitScraper
from scripts.ingestion.sources.dbe_south_africa import DBESouthAfricaScraper
from scripts.ingestion.sources.huggingface_datasets import HuggingFaceDatasetsScraper
from scripts.ingestion.sources.khan_academy import KhanAcademyScraper
from scripts.ingestion.sources.libretexts import LibreTextsScraper
from scripts.ingestion.sources.openstax import OpenStaxScraper
from scripts.ingestion.sources.siyavula import SiyavulaScraper
from scripts.ingestion.sources.wced import WCEDScraper

# ── Registry ──────────────────────────────────────────────────────────────────

SCRAPER_REGISTRY: dict[str, type[BaseScraper]] = {
    "khan_academy":        KhanAcademyScraper,
    "openstax":            OpenStaxScraper,
    "ck12":                CK12Scraper,
    "bbc_bitesize":        BBCBitesizeScraper,
    "commonlit":           CommonLitScraper,
    "libretexts":          LibreTextsScraper,
    "siyavula":            SiyavulaScraper,
    "dbe":                 DBESouthAfricaScraper,
    "wced":                WCEDScraper,
    "huggingface":         HuggingFaceDatasetsScraper,
}

# ── Convenience groups ────────────────────────────────────────────────────────

#: Sources that carry ZA-specific / CAPS-aligned content
ZA_SOURCES: list[str] = ["siyavula", "dbe", "wced"]

#: Global open-licensed sources (safe to redistribute training data)
OPEN_SOURCES: list[str] = [
    "khan_academy", "openstax", "ck12", "libretexts", "huggingface",
]

#: Sources that require Playwright (JS-heavy pages)
PLAYWRIGHT_SOURCES: list[str] = ["bbc_bitesize"]


def get_scraper(source_id: str, **kwargs: Any) -> BaseScraper:
    """
    Instantiate a scraper for *source_id*.

    Keyword args are forwarded to the scraper constructor
    (e.g. ``grade_range``, ``limit``, ``progress_cb``).

    Raises ``KeyError`` for unknown source IDs.
    """
    cls = SCRAPER_REGISTRY[source_id]
    return cls(**kwargs)


def list_sources() -> list[str]:
    """Return all registered source IDs."""
    return sorted(SCRAPER_REGISTRY.keys())


__all__ = [
    # Registry
    "SCRAPER_REGISTRY",
    "ZA_SOURCES",
    "OPEN_SOURCES",
    "PLAYWRIGHT_SOURCES",
    "get_scraper",
    "list_sources",
    # Base class
    "BaseScraper",
    # Scrapers
    "KhanAcademyScraper",
    "OpenStaxScraper",
    "CK12Scraper",
    "BBCBitesizeScraper",
    "CommonLitScraper",
    "LibreTextsScraper",
    "SiyavulaScraper",
    "DBESouthAfricaScraper",
    "WCEDScraper",
    "HuggingFaceDatasetsScraper",
]
