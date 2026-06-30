"""
Abstract base scraper — every source driver extends this.

Provides:
  • robots.txt compliance check before each request
  • Automatic rate limiting (token bucket)
  • Exponential back-off with jitter on 429/5xx
  • aiohttp session management
  • Progress callback hooks
  • Optional Playwright support for JS-heavy pages
"""
from __future__ import annotations

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Callable

import aiohttp

from scripts.ingestion.config import SourceConfig
from scripts.ingestion.models import RawContent
from scripts.ingestion.utils.rate_limiter import throttle
from scripts.ingestion.utils.robots_checker import can_fetch

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int, str], None]  # (done, total, msg)

_MAX_RETRIES   = 4
_BACKOFF_BASE  = 2.0
_BACKOFF_JITTER = 0.5


class BaseScraper(ABC):
    """
    Async base class for all curriculum source scrapers.

    Subclasses must implement :meth:`scrape` which yields
    :class:`~scripts.ingestion.models.RawContent` objects.
    """

    def __init__(
        self,
        config: SourceConfig,
        grade_range: tuple[int, int] = (1, 12),
        limit: int = 0,
        progress_cb: ProgressCallback | None = None,
    ) -> None:
        self.config      = config
        self.grade_range = grade_range
        self.limit       = limit          # 0 = unlimited
        self._progress   = progress_cb
        self._session: aiohttp.ClientSession | None = None
        self._done   = 0
        self._total  = 0

    # ── Session management ───────────────────────────────────────────────────

    async def __aenter__(self) -> "BaseScraper":
        self._session = aiohttp.ClientSession(
            headers={"User-Agent": self._user_agent},
            timeout=aiohttp.ClientTimeout(total=30),
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._session:
            await self._session.close()

    @property
    def _user_agent(self) -> str:
        return (
            "EduBoostSA-Ingestion/1.0 "
            "(+https://github.com/nkgolomatjila-svg/Eduboost_V.2; "
            "educational data collection, non-commercial)"
        )

    # ── Abstract interface ───────────────────────────────────────────────────

    @abstractmethod
    async def scrape(self) -> AsyncIterator[RawContent]:
        """Yield raw content items from this source."""
        ...  # pragma: no cover

    # ── HTTP helpers ─────────────────────────────────────────────────────────

    async def _get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any] | str | None:
        """
        Rate-limited, robots-compliant GET that returns parsed JSON or text.
        Retries on transient errors with exponential back-off.
        """
        assert self._session is not None, "Use 'async with scraper:'"

        # robots.txt gate
        allowed = await can_fetch(url, self.config.robots_txt_url)
        if not allowed:
            logger.warning("robots.txt disallows %s — skipping", url)
            return None

        # token-bucket throttle
        await throttle(self.config.id, self.config.rate_limit_rps)

        for attempt in range(_MAX_RETRIES):
            try:
                async with self._session.get(url, params=params, headers=headers) as resp:
                    if resp.status == 429:
                        wait = self._backoff(attempt)
                        logger.info("429 from %s — waiting %.1fs", url, wait)
                        await asyncio.sleep(wait)
                        continue
                    if resp.status >= 500:
                        wait = self._backoff(attempt)
                        logger.warning("5xx (%d) from %s — waiting %.1fs", resp.status, url, wait)
                        await asyncio.sleep(wait)
                        continue
                    if resp.status == 404:
                        return None
                    resp.raise_for_status()

                    content_type = resp.headers.get("Content-Type", "")
                    if "json" in content_type:
                        return await resp.json(content_type=None)

                    # Try normal text decode first; if that fails fall back to
                    # trying a few common encodings and finally a replace-mode
                    # UTF-8 decode to avoid crashing on malformed pages.
                    try:
                        return await resp.text()
                    except UnicodeDecodeError:
                        raw = await resp.read()
                        # Common fallbacks observed in the wild
                        for enc in ("utf-8", "windows-1252", "iso-8859-1"):
                            try:
                                text = raw.decode(enc)
                                logger.warning("Decoded %s using %s fallback", url, enc)
                                return text
                            except Exception:
                                continue
                        logger.warning("Unable to decode %s with common encodings; using replacement decoding", url)
                        return raw.decode("utf-8", errors="replace")

            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                wait = self._backoff(attempt)
                logger.warning("Request failed (%s) for %s — retry %d in %.1fs",
                               exc, url, attempt + 1, wait)
                await asyncio.sleep(wait)

        logger.error("All retries exhausted for %s", url)
        return None

    @staticmethod
    def _backoff(attempt: int) -> float:
        return _BACKOFF_BASE ** attempt + random.uniform(0, _BACKOFF_JITTER)

    # ── Progress reporting ────────────────────────────────────────────────────

    def _emit(self, done: int, total: int, message: str = "") -> None:
        self._done  = done
        self._total = total
        if self._progress:
            self._progress(done, total, message)

    # ── Playwright helper (JS-heavy pages) ───────────────────────────────────

    async def _playwright_get(self, url: str) -> str | None:
        """Fetch page HTML via Playwright (headless Chromium)."""
        try:
            from playwright.async_api import async_playwright  # type: ignore
        except ImportError:
            logger.error("playwright not installed — run: pip install playwright && playwright install chromium")
            return None

        allowed = await can_fetch(url, self.config.robots_txt_url)
        if not allowed:
            logger.warning("robots.txt disallows %s — skipping", url)
            return None

        await throttle(self.config.id, self.config.rate_limit_rps)

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page    = await browser.new_page(user_agent=self._user_agent)
            try:
                await page.goto(url, wait_until="networkidle", timeout=30_000)
                html = await page.content()
            finally:
                await browser.close()
        return html

    async def _playwright_capture(self, url: str, capture_xhr: bool = True) -> tuple[str | None, list[dict]]:
        """Fetch page HTML via Playwright and capture network responses (XHR/fetch).

        Returns a tuple of (html, responses) where `responses` is a list of
        dictionaries containing `url`, `status`, `resource_type`, `headers`,
        and optionally `body` for JSON/XHR payloads. This helper is intended
        for debugging JS-heavy SPAs to discover XHR endpoints used to populate
        the DOM (e.g. TOC JSON APIs).
        """
        try:
            from playwright.async_api import async_playwright  # type: ignore
        except ImportError:
            logger.error("playwright not installed — run: pip install playwright && playwright install chromium")
            return None, []

        allowed = await can_fetch(url, self.config.robots_txt_url)
        if not allowed:
            logger.warning("robots.txt disallows %s — skipping", url)
            return None, []

        await throttle(self.config.id, self.config.rate_limit_rps)

        responses: list[dict] = []
        async with async_playwright() as pw:
            pending_reads: list[asyncio.Task[None]] = []
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page(user_agent=self._user_agent)

            def _on_response(response):
                # Schedule reading the response body asynchronously so the
                # event handler remains non-blocking.
                async def _read():
                    try:
                        r_url = response.url
                        status = response.status
                        headers = dict(response.headers)
                        resource_type = response.request.resource_type
                        ct = headers.get("content-type", "")
                        body = None
                        if capture_xhr and (resource_type in ("xhr", "fetch") or "json" in ct or r_url.endswith(".json")):
                            try:
                                logger.debug("[Playwright capture] reading response body: %s", r_url)
                                body = await response.text()
                            except Exception:
                                body = None
                        responses.append({
                            "url": r_url,
                            "status": status,
                            "resource_type": resource_type,
                            "headers": headers,
                            "method": response.request.method,
                            "body": body,
                        })
                    except Exception:
                        # best-effort; swallow errors to avoid breaking navigation
                        return

                try:
                    pending_reads.append(asyncio.create_task(_read()))
                except Exception:
                    # If scheduling fails, ignore and continue
                    pass

            page.on("response", _on_response)
            try:
                await page.goto(url, wait_until="networkidle", timeout=30_000)
                html = await page.content()
                if pending_reads:
                    await asyncio.gather(*pending_reads, return_exceptions=True)
            finally:
                await browser.close()

        logger.info("[Playwright capture] captured %d network responses for %s", len(responses), url)

        return html, responses

    # ── Shared utilities ──────────────────────────────────────────────────────

    def _within_grade_range(self, grade: int | None) -> bool:
        if grade is None:
            return True
        lo, hi = self.grade_range
        return lo <= grade <= hi

    def _at_limit(self) -> bool:
        return self.limit > 0 and self._done >= self.limit
