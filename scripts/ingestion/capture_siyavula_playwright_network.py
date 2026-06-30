"""Capture rendered Siyavula HTML and Playwright network responses.

This is a targeted diagnostic for Siyavula's client-rendered book pages. It
uses the same scraper configuration, user agent, robots check, and rate limiter
as the ingestion pipeline, then persists the rendered HTML and response ledger.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from scripts.ingestion.sources.siyavula import SiyavulaScraper

DEFAULT_BOOK_URL = "https://www.siyavula.com/read/maths/grade-7"
DEFAULT_OUT_DIR = Path("artifacts/ingestion/siyavula_playwright")


def _slug_for_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_") or "root"
    return f"{parsed.netloc}_{path}".replace(".", "_").replace("-", "_")


def _serialise_response(response: dict) -> dict:
    body = response.get("body")
    body_preview = None
    body_json = None
    if isinstance(body, str):
        body_preview = body[:4000]
        content_type = response.get("headers", {}).get("content-type", "")
        if "json" in content_type:
            try:
                body_json = json.loads(body)
            except json.JSONDecodeError:
                body_json = None

    return {
        "url": response.get("url"),
        "status": response.get("status"),
        "method": response.get("method"),
        "resource_type": response.get("resource_type"),
        "content_type": response.get("headers", {}).get("content-type"),
        "body_bytes": len(body.encode("utf-8")) if isinstance(body, str) else 0,
        "body_preview": body_preview,
        "body_json": body_json,
    }


async def capture(url: str, out_dir: Path) -> tuple[Path, Path, int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug_for_url(url)
    html_path = out_dir / f"{slug}.html"
    network_path = out_dir / f"{slug}.network.json"

    scraper = SiyavulaScraper(grade_range=(7, 12), limit=0)
    html, responses = await scraper._playwright_capture(url, capture_xhr=True)
    if not html:
        raise RuntimeError(f"Playwright returned no HTML for {url}")

    html_path.write_text(html, encoding="utf-8")
    payload = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "url": url,
        "response_count": len(responses),
        "responses": [_serialise_response(r) for r in responses],
    }
    network_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return html_path, network_path, len(responses)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default=DEFAULT_BOOK_URL)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    html_path, network_path, count = asyncio.run(capture(args.url, args.out_dir))
    print(json.dumps({"html": str(html_path), "network": str(network_path), "responses": count}, indent=2))


if __name__ == "__main__":
    main()
