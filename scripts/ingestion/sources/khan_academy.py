"""
Khan Academy Scraper
====================
Collects Exercises and Articles for Grades 1–12.

The legacy ``/api/v1/topictree`` endpoint was removed (HTTP 410).  This
scraper discovers content links from rendered course pages via Playwright
and extracts lesson text / exercise metadata from each page.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, AsyncIterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scripts.ingestion.config import SOURCES, KA_TOPIC_TO_CAPS
from scripts.ingestion.models import RawContent
from scripts.ingestion.sources.base import BaseScraper

logger = logging.getLogger(__name__)

_KA_BASE = "https://www.khanacademy.org"

# Course landing pages that cover K–12 maths and sciences.
_COURSE_SEEDS: list[tuple[str, str]] = [
    ("/math/cc-kindergarten-math",           "math"),
    ("/math/cc-1st-grade-math",              "math"),
    ("/math/cc-2nd-grade-math",              "math"),
    ("/math/cc-third-grade-math",            "math"),
    ("/math/cc-fourth-grade-math",           "math"),
    ("/math/cc-fifth-grade-math",            "math"),
    ("/math/cc-sixth-grade-math",            "math"),
    ("/math/cc-seventh-grade-math",          "math"),
    ("/math/cc-eighth-grade-math",           "math"),
    ("/math/algebra",                        "math"),
    ("/math/geometry",                       "math"),
    ("/math/algebra2",                       "math"),
    ("/math/precalculus",                    "math"),
    ("/math/calculus-1",                     "math"),
    ("/math/statistics-probability",         "math"),
    ("/science/biology",                     "science"),
    ("/science/chemistry",                   "science"),
    ("/science/physics",                     "science"),
    ("/science/high-school-biology",         "science"),
    ("/science/chemistry-ap-chemistry",        "science"),
    ("/science/physics-ap-physics-1",        "science"),
    ("/computing/computer-science",          "computing"),
    ("/humanities/grammar",                  "humanities"),
]

_CONTENT_LINK_RE = re.compile(
    r'href="(/(?:math|science|computing|humanities|economics-finance-domain)[^"]+/(?:e|a)/[^"]+)"'
)


class KhanAcademyScraper(BaseScraper):
    """Scrapes Khan Academy via rendered course pages (Playwright)."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(config=SOURCES["khan_academy"], **kwargs)
        self._seen_links: set[str] = set()

    async def scrape(self) -> AsyncIterator[RawContent]:
        logger.info("[KhanAcademy] Discovering content links from course pages …")
        content_links = await self._discover_content_links()
        if not content_links:
            logger.error("[KhanAcademy] No content links discovered")
            return

        self._total = len(content_links)
        logger.info("[KhanAcademy] Found %d exercise/article links", self._total)

        for i, (path, kind) in enumerate(content_links):
            if self._at_limit():
                break
            self._emit(i, self._total, path.rsplit("/", 1)[-1])
            item = await self._fetch_content(path, kind)
            if item:
                self._done += 1
                yield item

    async def _discover_content_links(self) -> list[tuple[str, str]]:
        links: list[tuple[str, str]] = []
        grade_lo, grade_hi = self.grade_range
        for seed_path, _domain in _COURSE_SEEDS:
            if self._at_limit():
                break
            if not self._seed_matches_grade(seed_path, grade_lo, grade_hi):
                continue
            url  = f"{_KA_BASE}{seed_path}"
            html = await self._playwright_get(url)
            if not html:
                continue
            for match in _CONTENT_LINK_RE.findall(html):
                if match in self._seen_links:
                    continue
                if not self._path_matches_grade(match, grade_lo, grade_hi):
                    continue
                self._seen_links.add(match)
                kind = "exercise" if "/e/" in match else "article"
                links.append((match, kind))
        return links

    @staticmethod
    def _seed_matches_grade(seed_path: str, lo: int, hi: int) -> bool:
        """Skip kindergarten seeds when scraping grades 7+."""
        grade_hints = {
            "kindergarten": 0, "1st-grade": 1, "2nd-grade": 2, "third-grade": 3,
            "fourth-grade": 4, "fifth-grade": 5, "sixth-grade": 6,
            "seventh-grade": 7, "eighth-grade": 8,
        }
        for hint, g in grade_hints.items():
            if hint in seed_path:
                return lo <= g <= hi
        return True   # algebra, biology, etc. — include for grades 7+

    @staticmethod
    def _path_matches_grade(path: str, lo: int, hi: int) -> bool:
        if "kindergarten" in path and lo > 1:
            return False
        if "1st-grade" in path and (lo > 1 or hi < 1):
            return False
        if "2nd-grade" in path and (lo > 2 or hi < 2):
            return False
        if "third-grade" in path and (lo > 3 or hi < 3):
            return False
        if "fourth-grade" in path and (lo > 4 or hi < 4):
            return False
        if "fifth-grade" in path and (lo > 5 or hi < 5):
            return False
        if "sixth-grade" in path and (lo > 6 or hi < 6):
            return False
        if "seventh-grade" in path and (lo > 7 or hi < 7):
            return False
        if "eighth-grade" in path and (lo > 8 or hi < 8):
            return False
        return True

    async def _fetch_content(self, path: str, kind: str) -> RawContent | None:
        url  = urljoin(_KA_BASE, path)
        html = await self._playwright_get_ka(url)
        if not html:
            return None

        slug = path.rstrip("/").split("/")[-1]
        soup = BeautifulSoup(html, "html.parser")

        # Primary body: rendered article / lesson text from the page DOM.
        main_el = (
            soup.select_one("article")
            or soup.select_one("[data-test-id='article-content']")
            or soup.select_one("main")
        )
        plain = ""
        if main_el:
            plain = re.sub(
                r"\n{3,}", "\n\n",
                main_el.get_text(separator="\n", strip=True),
            ).strip()
        # Strip KA onboarding / login prompts that appear before content loads.
        plain = re.sub(
            r"^Skip to lesson content\s*Welcome to Khan Academy!.*?(?=Lesson \d:|Unit \d:|\Z)",
            "",
            plain,
            flags=re.DOTALL,
        ).strip()

        embedded = self._extract_embedded_json(html)
        title = (
            self._first_heading(soup)
            or embedded.get("translatedTitle")
            or embedded.get("title")
            or slug
        )
        if str(title).startswith("Welcome to Khan Academy"):
            title = self._first_heading(soup) or slug

        description = (
            embedded.get("translatedDescription")
            or embedded.get("description")
            or ""
        )

        if kind == "article":
            if len(plain) < 80:
                body_html = embedded.get("content") or embedded.get("htmlBody") or ""
                if body_html:
                    plain = BeautifulSoup(body_html, "html.parser").get_text(
                        separator="\n", strip=True
                    )
            if len(plain) < 80:
                return None
            topic_slug = self._topic_from_path(path)
            caps_meta  = KA_TOPIC_TO_CAPS.get(topic_slug, {})
            return RawContent(
                source_id          = "khan_academy",
                source_url         = url,
                source_internal_id = slug,
                raw_text           = plain,
                raw_html           = str(main_el) if main_el else None,
                raw_json           = {"node": embedded, "caps_meta": caps_meta},
                metadata           = {
                    "kind":        "article",
                    "title":       str(title)[:250],
                    "topic_slug":  topic_slug,
                    "caps_grades": caps_meta.get("grades"),
                    "caps_topic":  caps_meta.get("topic_code"),
                    "subject":     caps_meta.get("subject") or topic_slug,
                },
                license  = "CC BY-NC-SA 4.0",
                language = "en",
            )

        # Exercise — use page text when available; fall back to description.
        questions: list[dict[str, Any]] = []
        q_data = embedded.get("assessmentItem") or embedded.get("itemData")
        if q_data:
            parsed = self._parse_assessment_item({"item_data": q_data})
            if parsed:
                questions.append(parsed)

        body = plain if len(plain) >= 80 else (description or str(title))
        if questions:
            q_text = questions[0].get("question", "")
            if len(q_text) >= 40:
                body = q_text

        if len(body) < 40 or body.strip() == "Welcome to Khan Academy!":
            return None

        topic_slug = self._topic_from_path(path)
        caps_meta  = KA_TOPIC_TO_CAPS.get(topic_slug, {})
        return RawContent(
            source_id          = "khan_academy",
            source_url         = url,
            source_internal_id = slug,
            raw_text           = body,
            raw_json           = {
                "questions": questions,
                "node":      embedded,
                "caps_meta": caps_meta,
            },
            metadata           = {
                "kind":        "exercise",
                "title":       str(title)[:250],
                "topic_slug":  topic_slug,
                "caps_grades": caps_meta.get("grades"),
                "caps_topic":  caps_meta.get("topic_code"),
                "subject":     caps_meta.get("subject") or topic_slug,
            },
            license  = "CC BY-NC-SA 4.0",
            language = "en",
        )

    async def _playwright_get_ka(self, url: str) -> str | None:
        """Playwright fetch with KA onboarding modal dismissal."""
        try:
            from playwright.async_api import async_playwright  # type: ignore
        except ImportError:
            return await self._playwright_get(url)

        from scripts.ingestion.utils.robots_checker import can_fetch
        from scripts.ingestion.utils.rate_limiter import throttle

        allowed = await can_fetch(url, self.config.robots_txt_url)
        if not allowed:
            return None
        await throttle(self.config.id, self.config.rate_limit_rps)

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page    = await browser.new_page(user_agent=self._user_agent)
            try:
                await page.goto(url, wait_until="networkidle", timeout=45_000)
                for sel in (
                    "#onetrust-accept-btn-handler",
                    "button:has-text('Accept all')",
                    "button:has-text('Got it')",
                    "button:has-text('Continue')",
                ):
                    try:
                        loc = page.locator(sel).first
                        if await loc.count() > 0:
                            await loc.click(timeout=1500)
                    except Exception:
                        pass
                await page.wait_for_timeout(1500)
                return await page.content()
            finally:
                await browser.close()

    @staticmethod
    def _extract_embedded_json(html: str) -> dict[str, Any]:
        """Pull the first useful JSON blob from KA page scripts."""
        for pattern in (
            r'"contentModel"\s*:\s*(\{.*?\})\s*,\s*"',
            r'"learnableContent"\s*:\s*(\{.*?\})\s*,\s*"',
        ):
            m = re.search(pattern, html, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(1))
                except json.JSONDecodeError:
                    continue
        return {}

    @staticmethod
    def _first_heading(soup: BeautifulSoup) -> str | None:
        el = soup.select_one("h1, h2")
        return el.get_text(strip=True)[:250] if el else None

    @staticmethod
    def _topic_from_path(path: str) -> str:
        parts = [p for p in path.split("/") if p and p not in {"e", "a"}]
        return parts[1] if len(parts) >= 2 else (parts[0] if parts else "")

    @staticmethod
    def _parse_assessment_item(ai: dict[str, Any]) -> dict[str, Any] | None:
        try:
            item_data = ai.get("item_data") or ai
            if isinstance(item_data, str):
                item_data = json.loads(item_data)

            question = item_data.get("question", {})
            q_text   = BeautifulSoup(
                question.get("content", ""), "html.parser"
            ).get_text(strip=True)

            answers  = item_data.get("answers", [])
            options  = [
                BeautifulSoup(a.get("content", ""), "html.parser").get_text(strip=True)
                for a in answers
            ]
            correct_indices = [i for i, a in enumerate(answers) if a.get("correct")]
            correct = options[correct_indices[0]] if correct_indices and options else None

            hints = [
                BeautifulSoup(h.get("content", ""), "html.parser").get_text(strip=True)
                for h in item_data.get("hints", [])
            ]

            if not q_text:
                return None
            return {
                "question":    q_text,
                "options":     options,
                "answer":      correct,
                "explanation": "\n".join(hints),
            }
        except Exception:  # noqa: BLE001
            return None
