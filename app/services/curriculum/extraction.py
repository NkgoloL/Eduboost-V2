"""Structured extraction primitives for Phase 2R Gate 2R.3."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ExtractionRejectedError(ValueError):
    pass


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str
    text_sha256: str
    language: str
    extraction_confidence: float
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExtractedSection:
    section_order: int
    heading: str | None
    page_start: int
    page_end: int
    text_sha256: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChunkProposal:
    chunk_order: int
    page_start: int
    page_end: int
    text: str
    text_sha256: str
    section_heading: str | None
    language: str
    quality_score: float


@dataclass(frozen=True)
class ExtractionResult:
    pages: list[ExtractedPage]
    sections: list[ExtractedSection]
    chunks: list[ChunkProposal]
    text_sha256: str
    warnings: list[str]


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class StructuredTextExtractor:
    """Deterministic text-fixture extractor with page and chunk provenance.

    Native PDF extraction should be implemented by a production adapter that
    returns the same result contract. OCR remains a review-required fallback.
    """

    def __init__(self, *, max_chunk_chars: int = 1200) -> None:
        self.max_chunk_chars = max_chunk_chars

    def extract_text_fixture(self, path: str | Path, *, language: str) -> ExtractionResult:
        if language not in {"en", "af", "nso"}:
            raise ExtractionRejectedError("language must be one of en, af, nso")
        raw = Path(path).read_text(encoding="utf-8")
        if not raw.strip():
            raise ExtractionRejectedError("source text is empty")
        page_texts = [page.strip() for page in raw.split("\f")]
        page_texts = [page for page in page_texts if page]
        pages = [
            ExtractedPage(
                page_number=index + 1,
                text=text,
                text_sha256=_sha(text),
                language=language,
                extraction_confidence=1.0,
            )
            for index, text in enumerate(page_texts)
        ]
        chunks = self._chunk_pages(pages, language=language)
        sections = [
            ExtractedSection(
                section_order=index,
                heading=chunk.section_heading,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                text_sha256=chunk.text_sha256,
            )
            for index, chunk in enumerate(chunks)
        ]
        return ExtractionResult(
            pages=pages,
            sections=sections,
            chunks=chunks,
            text_sha256=_sha("\n".join(page.text for page in pages)),
            warnings=[],
        )

    def _chunk_pages(self, pages: list[ExtractedPage], *, language: str) -> list[ChunkProposal]:
        chunks: list[ChunkProposal] = []
        current: list[str] = []
        page_start = pages[0].page_number
        last_page = page_start
        for page in pages:
            for paragraph in [part.strip() for part in page.text.split("\n\n") if part.strip()]:
                if current and sum(len(item) for item in current) + len(paragraph) > self.max_chunk_chars:
                    text = "\n\n".join(current)
                    chunks.append(
                        ChunkProposal(
                            chunk_order=len(chunks),
                            page_start=page_start,
                            page_end=last_page,
                            text=text,
                            text_sha256=_sha(text),
                            section_heading=_heading(current[0]),
                            language=language,
                            quality_score=1.0,
                        )
                    )
                    current = []
                    page_start = page.page_number
                current.append(paragraph)
                last_page = page.page_number
        if current:
            text = "\n\n".join(current)
            chunks.append(
                ChunkProposal(
                    chunk_order=len(chunks),
                    page_start=page_start,
                    page_end=last_page,
                    text=text,
                    text_sha256=_sha(text),
                    section_heading=_heading(current[0]),
                    language=language,
                    quality_score=1.0,
                )
            )
        return chunks


def _heading(text: str) -> str | None:
    first_line = text.splitlines()[0].strip() if text.splitlines() else ""
    if 0 < len(first_line) <= 120 and (first_line.isupper() or first_line.endswith(":")):
        return first_line.rstrip(":")
    return None
