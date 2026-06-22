"""Structured extraction primitives for Phase 2R Gate 2R.3.

Gate 2R.3 is intentionally limited to extraction, page/section provenance,
chunk proposals, and extraction-quality warnings. It does not approve mappings,
freeze a corpus, activate retrieval, or authorise generation.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

ALLOWED_LANGUAGES = frozenset({"en", "af", "nso"})
PROMPT_INJECTION_PATTERNS = (
    "ignore previous instructions",
    "system prompt",
    "developer message",
    "act as",
    "jailbreak",
)


class ExtractionRejectedError(ValueError):
    """Raised when extraction input or output cannot pass Gate 2R.3 controls."""


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str
    text_sha256: str
    language: str
    extraction_confidence: float
    warnings: list[str] = field(default_factory=list)
    coordinate_metadata: dict[str, Any] = field(default_factory=dict)


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
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExtractionResult:
    pages: list[ExtractedPage]
    sections: list[ExtractedSection]
    chunks: list[ChunkProposal]
    text_sha256: str
    warnings: list[str]
    extraction_mode: str = "text_fixture"
    extractor_name: str = "structured_text_extractor"
    extractor_version: str = "gate2r3-v1"
    quality_score: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalise_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"\n{4,}", "\n\n\n", value)
    return value.strip()


def _validate_language(language: str) -> None:
    if language not in ALLOWED_LANGUAGES:
        raise ExtractionRejectedError("language must be one of en, af, nso")


def _page_warnings(text: str) -> list[str]:
    warnings: list[str] = []
    stripped = text.strip()
    if not stripped:
        warnings.append("no_extractable_text")
    if 0 < len(stripped) < 40:
        warnings.append("very_low_text_density")
    if re.search(r"\d+\s*[+\-x×÷/=]\s*\d+", text):
        warnings.append("formula_or_arithmetic_expression_detected")
    aligned_rows = 0
    for line in text.splitlines():
        cells = [cell for cell in re.split(r"\s{2,}|\t+", line.strip()) if cell]
        if len(cells) >= 3:
            aligned_rows += 1
    if aligned_rows >= 3:
        warnings.append("possible_table_or_aligned_columns_detected")
    lowered = text.lower()
    if any(pattern in lowered for pattern in PROMPT_INJECTION_PATTERNS):
        warnings.append("possible_source_embedded_prompt_injection")
    return warnings


def _confidence_for_text(text: str, warnings: list[str]) -> float:
    if "no_extractable_text" in warnings:
        return 0.0
    score = 1.0
    if "very_low_text_density" in warnings:
        score -= 0.25
    if "possible_table_or_aligned_columns_detected" in warnings:
        score -= 0.1
    if "formula_or_arithmetic_expression_detected" in warnings:
        score -= 0.05
    if "possible_source_embedded_prompt_injection" in warnings:
        score -= 0.35
    return max(0.0, round(score, 3))


def _heading(text: str) -> str | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None
    first_line = lines[0]
    if len(first_line) > 160:
        return None
    if first_line.isupper() and any(ch.isalpha() for ch in first_line):
        return first_line.rstrip(":")
    if first_line.endswith(":") and len(first_line) <= 120:
        return first_line.rstrip(":")
    if re.match(r"^(\d+(\.\d+)*|[A-Z])\s+[A-Z][A-Za-z0-9,;:()\-/ ]{4,}$", first_line):
        return first_line
    return None


def _split_paragraphs(text: str) -> list[str]:
    chunks = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if len(chunks) <= 1:
        chunks = [part.strip() for part in text.splitlines() if part.strip()]
    return chunks


class StructuredTextExtractor:
    """Deterministic extraction and structure-aware chunking adapter.

    The text-fixture mode is used by fast unit tests. Native PDF mode uses
    pypdf when available and returns the same result contract.
    """

    def __init__(self, *, max_chunk_chars: int = 1200, min_chunk_chars: int = 80) -> None:
        if max_chunk_chars < 120:
            raise ExtractionRejectedError("max_chunk_chars must be at least 120")
        if min_chunk_chars < 0:
            raise ExtractionRejectedError("min_chunk_chars cannot be negative")
        self.max_chunk_chars = max_chunk_chars
        self.min_chunk_chars = min_chunk_chars

    def extract_text_fixture(self, path: str | Path, *, language: str) -> ExtractionResult:
        _validate_language(language)
        source = Path(path)
        if not source.is_file():
            raise ExtractionRejectedError(f"source text fixture does not exist: {source}")
        raw = source.read_text(encoding="utf-8")
        return self.extract_pages([_normalise_text(page) for page in raw.split("\f")], language=language, extraction_mode="text_fixture")

    def extract_pdf(self, path: str | Path, *, language: str, max_pages: int | None = None) -> ExtractionResult:
        _validate_language(language)
        source = Path(path)
        if not source.is_file():
            raise ExtractionRejectedError(f"source PDF does not exist: {source}")
        if source.suffix.lower() != ".pdf":
            raise ExtractionRejectedError("native PDF extraction requires a .pdf source")
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover - environment guard
            raise ExtractionRejectedError("pypdf is required for native_pdf extraction") from exc

        reader = PdfReader(str(source))
        limit = len(reader.pages) if max_pages is None else min(max_pages, len(reader.pages))
        if limit <= 0:
            raise ExtractionRejectedError("PDF contains no pages to extract")
        pages: list[str] = []
        pdf_warnings: list[str] = []
        if getattr(reader, "is_encrypted", False):
            try:
                reader.decrypt("")
                pdf_warnings.append("pdf_was_encrypted_empty_password_accepted")
            except Exception as exc:
                raise ExtractionRejectedError("encrypted PDF could not be decrypted") from exc
        for index in range(limit):
            text = reader.pages[index].extract_text() or ""
            pages.append(_normalise_text(text))
        result = self.extract_pages(pages, language=language, extraction_mode="native_pdf")
        return ExtractionResult(
            pages=result.pages,
            sections=result.sections,
            chunks=result.chunks,
            text_sha256=result.text_sha256,
            warnings=sorted(set(result.warnings + pdf_warnings)),
            extraction_mode="native_pdf",
            extractor_name="pypdf_structured_extractor",
            extractor_version=getattr(__import__("pypdf"), "__version__", "unknown"),
            quality_score=result.quality_score,
            metadata={"page_count_extracted": limit, "page_count_total": len(reader.pages)},
        )

    def extract_pages(self, page_texts: Iterable[str], *, language: str, extraction_mode: str) -> ExtractionResult:
        _validate_language(language)
        pages: list[ExtractedPage] = []
        for index, text in enumerate(page_texts, start=1):
            normalised = _normalise_text(text)
            warnings = _page_warnings(normalised)
            pages.append(
                ExtractedPage(
                    page_number=index,
                    text=normalised,
                    text_sha256=_sha(normalised),
                    language=language,
                    extraction_confidence=_confidence_for_text(normalised, warnings),
                    warnings=warnings,
                    coordinate_metadata={"source_page_index": index - 1},
                )
            )
        if not pages:
            raise ExtractionRejectedError("source produced zero pages")
        if all(not page.text for page in pages):
            raise ExtractionRejectedError("source produced no extractable text")

        chunks = self._chunk_pages([page for page in pages if page.text], language=language)
        if not chunks:
            raise ExtractionRejectedError("source produced zero chunks")
        sections = self._sections_from_chunks(chunks)
        warnings = sorted({warning for page in pages for warning in page.warnings} | {warning for chunk in chunks for warning in chunk.warnings})
        confidence_values = [page.extraction_confidence for page in pages]
        quality = round(sum(confidence_values) / len(confidence_values), 3)
        return ExtractionResult(
            pages=pages,
            sections=sections,
            chunks=chunks,
            text_sha256=_sha("\n\f\n".join(page.text for page in pages)),
            warnings=warnings,
            extraction_mode=extraction_mode,
            quality_score=quality,
            metadata={"page_count": len(pages), "chunk_count": len(chunks)},
        )

    def _chunk_pages(self, pages: list[ExtractedPage], *, language: str) -> list[ChunkProposal]:
        chunks: list[ChunkProposal] = []
        current: list[str] = []
        current_warnings: set[str] = set()
        page_start = pages[0].page_number
        last_page = page_start

        def flush() -> None:
            nonlocal current, current_warnings, page_start, last_page
            if not current:
                return
            text = "\n\n".join(current).strip()
            if not text:
                current = []
                current_warnings = set()
                return
            quality = 1.0
            if len(text) < self.min_chunk_chars:
                current_warnings.add("short_chunk_review_recommended")
                quality -= 0.15
            if "possible_table_or_aligned_columns_detected" in current_warnings:
                quality -= 0.1
            if "formula_or_arithmetic_expression_detected" in current_warnings:
                quality -= 0.05
            if "possible_source_embedded_prompt_injection" in current_warnings:
                quality -= 0.35
            chunks.append(
                ChunkProposal(
                    chunk_order=len(chunks),
                    page_start=page_start,
                    page_end=last_page,
                    text=text,
                    text_sha256=_sha(text),
                    section_heading=_heading(current[0]),
                    language=language,
                    quality_score=max(0.0, round(quality, 3)),
                    warnings=sorted(current_warnings),
                    metadata={"paragraph_count": len(current)},
                )
            )
            current = []
            current_warnings = set()

        for page in pages:
            paragraphs = _split_paragraphs(page.text)
            for paragraph in paragraphs:
                next_length = len("\n\n".join(current + [paragraph]))
                paragraph_heading = _heading(paragraph)
                current_heading = _heading(current[0]) if current else None
                heading_changed = bool(current and paragraph_heading and paragraph_heading != current_heading)
                if current and (next_length > self.max_chunk_chars or heading_changed):
                    flush()
                    page_start = page.page_number
                current.append(paragraph)
                current_warnings.update(page.warnings)
                last_page = page.page_number
        flush()
        return chunks

    def _sections_from_chunks(self, chunks: list[ChunkProposal]) -> list[ExtractedSection]:
        sections: list[ExtractedSection] = []
        for chunk in chunks:
            sections.append(
                ExtractedSection(
                    section_order=len(sections),
                    heading=chunk.section_heading,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    text_sha256=chunk.text_sha256,
                    metadata={"chunk_order": chunk.chunk_order, "quality_score": chunk.quality_score},
                )
            )
        return sections


def validate_extraction_result(result: ExtractionResult, *, min_quality_score: float = 0.5) -> list[str]:
    """Return closure-grade validation errors for a Gate 2R.3 extraction result."""

    errors: list[str] = []
    if not result.pages:
        errors.append("extraction result has no pages")
    if not result.sections:
        errors.append("extraction result has no sections")
    if not result.chunks:
        errors.append("extraction result has no chunks")
    if result.quality_score < min_quality_score:
        errors.append("extraction quality score is below threshold")
    page_numbers = [page.page_number for page in result.pages]
    if page_numbers != sorted(page_numbers) or len(page_numbers) != len(set(page_numbers)):
        errors.append("page numbers must be unique and increasing")
    page_set = set(page_numbers)
    for page in result.pages:
        if not re.fullmatch(r"[0-9a-f]{64}", page.text_sha256):
            errors.append(f"page {page.page_number} has invalid text_sha256")
        if page.language not in ALLOWED_LANGUAGES:
            errors.append(f"page {page.page_number} has invalid language")
    for chunk in result.chunks:
        if chunk.language not in ALLOWED_LANGUAGES:
            errors.append(f"chunk {chunk.chunk_order} has invalid language")
        if not re.fullmatch(r"[0-9a-f]{64}", chunk.text_sha256):
            errors.append(f"chunk {chunk.chunk_order} has invalid text_sha256")
        if chunk.page_start not in page_set or chunk.page_end not in page_set or chunk.page_end < chunk.page_start:
            errors.append(f"chunk {chunk.chunk_order} has invalid page range")
        if not chunk.text.strip():
            errors.append(f"chunk {chunk.chunk_order} has empty text")
    return errors
