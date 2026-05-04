#!/usr/bin/env python3
"""
Scrape South African DBE CAPS PDFs and optionally upload them to Cloudflare R2.

Examples:
  python scripts/scrape_caps.py --dry-run
  python scripts/scrape_caps.py --max-docs 10 --extract-text
  python scripts/scrape_caps.py --upload-r2 --extract-text

Environment for R2 upload:
  R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import mimetypes
import os
import re
import sys
import time
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.request import Request, urlopen
from urllib.parse import parse_qs, quote, unquote, urljoin, urlparse

try:
    import boto3
except ImportError:  # pragma: no cover - exercised by real runtime, not unit tests
    boto3 = None

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover
    fitz = None

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    BeautifulSoup = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

LOGGER = logging.getLogger("scrape_caps")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "caps"
DEFAULT_START_URLS = [
    "https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements/CAPSFoundation/tabid/571/Default.aspx",
    "https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements/CAPSIntermediate/tabid/572/Default.aspx",
    "https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements/CAPSSenior/tabid/573/Default.aspx",
]
ALLOWED_HOSTS = {"www.education.gov.za", "education.gov.za"}
PHASE_HINTS = {
    "foundation": "grades-r-3",
    "intermediate": "grades-4-6",
    "senior": "grades-7-9",
}


@dataclass(frozen=True)
class CapsDocument:
    title: str
    url: str
    source_page: str
    phase: str | None = None
    language: str | None = None
    subject: str | None = None

    @property
    def filename(self) -> str:
        parsed = urlparse(self.url)
        query = parse_qs(parsed.query)
        ticket = query.get("fileticket", [""])[0]
        stem_source = unquote(Path(parsed.path).name) or self.title or ticket or self.url
        if parsed.path.lower().endswith(".pdf"):
            stem_source = Path(stem_source).stem
        if not stem_source or stem_source.lower() == "linkclick.aspx":
            stem_source = self.title or ticket or stable_id(self.url)
        return f"{slugify(stem_source)[:120] or stable_id(self.url)}.pdf"

    @property
    def r2_key_prefix(self) -> str:
        phase = slugify(self.phase or "uncategorized")
        subject = slugify(self.subject or "general")
        language = slugify(self.language or "unknown-language")
        return f"training-data/raw/caps/{phase}/{subject}/{language}"


def stable_id(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def slugify(value: str) -> str:
    value = unquote(value).strip().lower()
    value = re.sub(r"&amp;|&", " and ", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-{2,}", "-", value).strip("-")


def infer_phase(source_page: str, title: str) -> str | None:
    probe = f"{source_page} {title}".lower()
    for hint, phase in PHASE_HINTS.items():
        if hint in probe:
            return phase
    if re.search(r"\bgrade\s*r\b|grades?\s*r\s*[-–]\s*3", probe):
        return "grades-r-3"
    if re.search(r"grades?\s*4\s*[-–]\s*6", probe):
        return "grades-4-6"
    if re.search(r"grades?\s*7\s*[-–]\s*9", probe):
        return "grades-7-9"
    return None


def normalize_url(href: str, base_url: str) -> str:
    absolute = urljoin(base_url, href)
    parsed = urlparse(absolute)
    path = quote(unquote(parsed.path), safe="/()%")
    query_parts = parse_qs(parsed.query, keep_blank_values=True)
    query_parts.pop("forcedownload", None)
    query = "&".join(
        f"{quote(key, safe='')}={quote(value, safe='')}"
        for key in sorted(query_parts)
        for value in query_parts[key]
    )
    return parsed._replace(path=path, query=query, fragment="").geturl()


def is_pdf_link(url: str, text: str = "") -> bool:
    parsed = urlparse(url)
    lowered = f"{parsed.path} {parsed.query} {text}".lower()
    return ".pdf" in lowered or "linkclick.aspx" in lowered and "fileticket=" in lowered


def parse_caps_documents(html: str, source_url: str) -> list[CapsDocument]:
    if BeautifulSoup is None:
        return parse_caps_documents_stdlib(html, source_url)

    soup = BeautifulSoup(html, "html.parser")
    docs: list[CapsDocument] = []
    seen: set[str] = set()

    for link in soup.find_all("a", href=True):
        href = str(link["href"]).strip()
        text = " ".join(link.get_text(" ", strip=True).split())
        url = normalize_url(href, source_url)
        host = urlparse(url).netloc.lower()
        if host not in ALLOWED_HOSTS or not is_pdf_link(url, text):
            continue

        title = text if text and not is_context_poor_title(text) else nearby_title(link)
        doc = CapsDocument(
            title=title or Path(urlparse(url).path).stem or stable_id(url),
            url=url,
            source_page=source_url,
            phase=infer_phase(source_url, title),
            language=infer_language(title),
            subject=infer_subject(title),
        )
        if doc.url not in seen:
            docs.append(doc)
            seen.add(doc.url)

    return docs


class CapsLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str, str]] = []
        self._href: str | None = None
        self._anchor_text: list[str] = []
        self._in_cell = False
        self._cell_text: list[str] = []
        self._row_cells: list[str] = []
        self._in_row = False
        self._heading_level: str | None = None
        self._heading_text: list[str] = []
        self._current_heading = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "tr":
            self._in_row = True
            self._row_cells = []
        elif tag in {"h1", "h2", "h3", "h4"}:
            self._heading_level = tag
            self._heading_text = []
        elif tag in {"td", "th"}:
            self._in_cell = True
            self._cell_text = []
        elif tag == "a" and attrs_dict.get("href"):
            self._href = attrs_dict["href"]
            self._anchor_text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._anchor_text.append(data)
        if self._in_cell:
            self._cell_text.append(data)
        if self._heading_level is not None:
            self._heading_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href is not None:
            row_title = " ".join(cell for cell in self._row_cells if cell.lower() != "download")
            context_title = " - ".join(part for part in [self._current_heading, row_title.strip()] if part)
            self.links.append((self._href, " ".join(self._anchor_text).strip(), context_title))
            self._href = None
            self._anchor_text = []
        elif tag == self._heading_level:
            self._current_heading = " ".join(" ".join(self._heading_text).split())
            self._heading_level = None
            self._heading_text = []
        elif tag in {"td", "th"} and self._in_cell:
            cell = " ".join(" ".join(self._cell_text).split())
            if cell:
                self._row_cells.append(cell)
            self._in_cell = False
            self._cell_text = []
        elif tag == "tr":
            self._in_row = False
            self._row_cells = []


def parse_caps_documents_stdlib(html: str, source_url: str) -> list[CapsDocument]:
    parser = CapsLinkParser()
    parser.feed(html)
    docs: list[CapsDocument] = []
    seen: set[str] = set()

    for href, text, row_title in parser.links:
        url = normalize_url(href.strip(), source_url)
        host = urlparse(url).netloc.lower()
        if host not in ALLOWED_HOSTS or not is_pdf_link(url, text):
            continue

        if text and not is_context_poor_title(text):
            title = text
        elif row_title and text and text.lower() != "download":
            title = " - ".join(part for part in [row_title, text] if part and part.lower() not in row_title.lower())
        else:
            title = row_title or "CAPS document"
        doc = CapsDocument(
            title=title,
            url=url,
            source_page=source_url,
            phase=infer_phase(source_url, title),
            language=infer_language(title),
            subject=infer_subject(title),
        )
        if doc.url not in seen:
            docs.append(doc)
            seen.add(doc.url)

    return docs


def is_context_poor_title(title: str) -> bool:
    normalized = title.strip().lower()
    return normalized == "download" or infer_language(normalized) == normalized


def nearby_title(link: object) -> str:
    row = getattr(link, "find_parent", lambda *_: None)("tr")
    heading = getattr(link, "find_previous", lambda *_: None)(["h1", "h2", "h3", "h4"])
    heading_text = ""
    if heading is not None:
        heading_text = " ".join(heading.get_text(" ", strip=True).split())
    if row is not None:
        cells = [" ".join(cell.get_text(" ", strip=True).split()) for cell in row.find_all(["td", "th"])]
        cells = [cell for cell in cells if cell and cell.lower() != "download"]
        if cells:
            return " - ".join(part for part in [heading_text, *cells] if part)
    if heading_text:
        return heading_text
    return "CAPS document"


def infer_language(title: str) -> str | None:
    languages = [
        "afrikaans",
        "english",
        "isindebele",
        "isixhosa",
        "isizulu",
        "sepedi",
        "sesotho",
        "setswana",
        "siswati",
        "tshivenda",
        "xitsonga",
    ]
    probe = title.lower()
    return next((language for language in languages if language in probe), None)


def infer_subject(title: str) -> str | None:
    subjects = [
        "coding and robotics",
        "home languages",
        "first additional language",
        "mathematics",
        "life skills",
        "natural sciences and technology",
        "social sciences",
        "creative arts",
        "economic management sciences",
        "technology",
        "life orientation",
    ]
    probe = title.lower()
    return next((subject for subject in subjects if subject in probe), None)


def fetch_page_html(url: str, timeout_ms: int) -> str:
    if sync_playwright is None:
        return fetch_page_html_stdlib(url, timeout_ms)

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            html = page.content()
            browser.close()
        return html
    except Exception as exc:  # pragma: no cover - depends on local browser install
        LOGGER.info("Playwright fetch failed for %s; falling back to urllib: %s", url, exc)
        return fetch_page_html_stdlib(url, timeout_ms)


def fetch_page_html_stdlib(url: str, timeout_ms: int) -> str:
    request = Request(url, headers={"User-Agent": "EduBoost-CAPS-Scraper/1.0"})
    with urlopen(request, timeout=timeout_ms / 1000) as response:
        return response.read().decode("utf-8", errors="replace")


def discover_documents(start_urls: Iterable[str], timeout_ms: int, delay_seconds: float) -> list[CapsDocument]:
    documents: list[CapsDocument] = []
    seen: set[str] = set()
    for url in start_urls:
        LOGGER.info("Discovering CAPS PDFs from %s", url)
        html = fetch_page_html(url, timeout_ms=timeout_ms)
        for doc in parse_caps_documents(html, url):
            if doc.url not in seen:
                documents.append(doc)
                seen.add(doc.url)
        time.sleep(delay_seconds)
    return documents


def download_file(url: str, destination: Path, timeout_ms: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if sync_playwright is None:
        download_file_stdlib(url, destination, timeout_ms)
        return

    try:
        with sync_playwright() as playwright:
            request = playwright.request.new_context()
            response = request.get(url, timeout=timeout_ms)
            if not response.ok:
                raise RuntimeError(f"Download failed ({response.status}) for {url}")
            destination.write_bytes(response.body())
            request.dispose()
    except Exception as exc:  # pragma: no cover - depends on local browser install
        LOGGER.info("Playwright download failed for %s; falling back to urllib: %s", url, exc)
        download_file_stdlib(url, destination, timeout_ms)


def download_file_stdlib(url: str, destination: Path, timeout_ms: int) -> None:
    request = Request(url, headers={"User-Agent": "EduBoost-CAPS-Scraper/1.0"})
    with urlopen(request, timeout=timeout_ms / 1000) as response:
        destination.write_bytes(response.read())


def extract_pdf_text(pdf_path: Path, text_path: Path) -> dict[str, int]:
    if fitz is None:
        raise RuntimeError("PyMuPDF is required for text extraction. Install it with: pip install PyMuPDF")

    text_path.parent.mkdir(parents=True, exist_ok=True)
    page_count = 0
    with fitz.open(pdf_path) as document:
        parts = []
        page_count = document.page_count
        for page in document:
            parts.append(page.get_text("text"))
    text = "\n\n".join(part.strip() for part in parts if part.strip())
    text_path.write_text(text, encoding="utf-8")
    return {"pages": page_count, "characters": len(text)}


def create_r2_client() -> object:
    if boto3 is None:
        raise RuntimeError("boto3 is required for R2 upload.")

    required = ["R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET_NAME"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing R2 environment variables: {', '.join(missing)}")

    return boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT_URL"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name=os.getenv("R2_REGION", "auto"),
    )


def upload_to_r2(client: object, local_path: Path, key: str) -> None:
    content_type = mimetypes.guess_type(local_path.name)[0] or "application/octet-stream"
    client.upload_file(
        str(local_path),
        os.environ["R2_BUCKET_NAME"],
        key,
        ExtraArgs={"ContentType": content_type},
    )


def write_manifest(output_dir: Path, records: list[dict[str, object]]) -> Path:
    manifest_path = output_dir / "manifest.jsonl"
    with manifest_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return manifest_path


def run(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s %(message)s")

    output_dir = Path(args.output_dir).resolve()
    start_urls = args.start_url or DEFAULT_START_URLS
    documents = discover_documents(start_urls, timeout_ms=args.timeout_ms, delay_seconds=args.delay_seconds)
    if args.max_docs:
        documents = documents[: args.max_docs]

    LOGGER.warning("Discovered %s CAPS PDF candidates", len(documents))
    if args.dry_run:
        for doc in documents:
            print(json.dumps(asdict(doc), ensure_ascii=False, sort_keys=True))
        return 0

    r2_client = create_r2_client() if args.upload_r2 else None
    records: list[dict[str, object]] = []

    for index, doc in enumerate(documents, start=1):
        pdf_path = output_dir / "pdf" / doc.r2_key_prefix.replace("/", os.sep) / doc.filename
        text_path = output_dir / "text" / doc.r2_key_prefix.replace("/", os.sep) / f"{pdf_path.stem}.txt"
        LOGGER.warning("[%s/%s] %s", index, len(documents), doc.title)
        download_file(doc.url, pdf_path, timeout_ms=args.timeout_ms)

        extraction: dict[str, int] | None = None
        if args.extract_text:
            extraction = extract_pdf_text(pdf_path, text_path)

        pdf_key = f"{doc.r2_key_prefix}/{doc.filename}"
        text_key = f"{doc.r2_key_prefix}/{pdf_path.stem}.txt"
        if r2_client is not None:
            upload_to_r2(r2_client, pdf_path, pdf_key)
            if args.extract_text:
                upload_to_r2(r2_client, text_path, text_key)

        record = {
            **asdict(doc),
            "local_pdf": str(pdf_path),
            "local_text": str(text_path) if args.extract_text else None,
            "r2_pdf_key": pdf_key if args.upload_r2 else None,
            "r2_text_key": text_key if args.upload_r2 and args.extract_text else None,
            "extraction": extraction,
            "sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
        }
        records.append(record)
        time.sleep(args.delay_seconds)

    manifest_path = write_manifest(output_dir, records)
    LOGGER.warning("Wrote manifest: %s", manifest_path)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scrape DBE CAPS PDFs for EduBoost training data.")
    parser.add_argument("--start-url", action="append", help="CAPS index page to scrape. Can be used multiple times.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Local output directory.")
    parser.add_argument("--max-docs", type=int, help="Limit documents for smoke runs.")
    parser.add_argument("--timeout-ms", type=int, default=60_000, help="Playwright navigation/download timeout.")
    parser.add_argument("--delay-seconds", type=float, default=1.0, help="Polite delay between pages/downloads.")
    parser.add_argument("--extract-text", action="store_true", help="Extract PDF text with PyMuPDF.")
    parser.add_argument("--upload-r2", action="store_true", help="Upload PDFs/text/manifest assets to Cloudflare R2.")
    parser.add_argument("--dry-run", action="store_true", help="Print discovered documents without downloading.")
    parser.add_argument("--verbose", action="store_true", help="Enable detailed logging.")
    return parser


def main(argv: list[str] | None = None) -> int:
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
