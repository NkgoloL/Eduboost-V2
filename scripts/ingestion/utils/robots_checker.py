"""Async robots.txt compliance checker."""
from __future__ import annotations

import asyncio
from urllib.robotparser import RobotFileParser

import aiohttp

_CACHE:  dict[str, RobotFileParser] = {}
_LOCKS:  dict[str, asyncio.Lock]    = {}
USER_AGENT = "EduBoostSA-Ingestion/1.0 (+https://github.com/nkgolomatjila-svg/Eduboost_V.2)"


async def _fetch_robots(robots_url: str) -> RobotFileParser:
    if robots_url not in _LOCKS:
        _LOCKS[robots_url] = asyncio.Lock()

    async with _LOCKS[robots_url]:
        if robots_url in _CACHE:
            return _CACHE[robots_url]

        rp = RobotFileParser(robots_url)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    text = await resp.text()
            rp.parse(text.splitlines())
        except Exception:
            # If we can't fetch robots.txt, allow everything (fail open)
            pass

        _CACHE[robots_url] = rp
        return rp


async def can_fetch(url: str, robots_txt_url: str) -> bool:
    """Return True if USER_AGENT is allowed to fetch *url*."""
    rp = await _fetch_robots(robots_txt_url)
    return rp.can_fetch(USER_AGENT, url)


def extract_crawl_delay(robots_txt_url: str) -> float | None:
    """Return crawl-delay seconds if declared in robots.txt, else None."""
    rp = _CACHE.get(robots_txt_url)
    if rp is None:
        return None
    delay = rp.crawl_delay(USER_AGENT)
    return float(delay) if delay else None
