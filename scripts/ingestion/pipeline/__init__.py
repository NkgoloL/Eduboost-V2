"""
EduBoost SA — Pipeline Orchestrator
=====================================
Chains the four processing stages into a single ``Pipeline`` object:

    Stage 1 │ Normaliser        RawContent       → NormalisedContent
    Stage 2 │ CAPSAligner       NormalisedContent (enriched in-place)
    Stage 3 │ TrainingFormatter NormalisedContent → TrainingRecord
    Stage 4 │ StorageLayer      persist all three artefacts

Usage::

    from scripts.ingestion.pipeline import Pipeline

    pipeline = Pipeline(db_url="postgresql+asyncpg://localhost/eduboost")
    await pipeline.init()

    async for raw in scraper.scrape():
        result = await pipeline.process(raw)
        if result:
            print(f"Stored training record {result.id}")

    stats = pipeline.stats()
    await pipeline.close()
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

from scripts.ingestion.models import (  # noqa: F401  (re-export for pipeline consumers)
    IngestionJob,
    JobStatus,
    NormalisedContent,
    RawContent,
    TrainingRecord,
)
from scripts.ingestion.pipeline.caps_aligner import align
from scripts.ingestion.pipeline.normaliser import normalise
from scripts.ingestion.pipeline.storage import StorageLayer
from scripts.ingestion.pipeline.training_formatter import format_record

logger = logging.getLogger(__name__)


# ── Pipeline Statistics ───────────────────────────────────────────────────────

@dataclass
class PipelineStats:
    scraped:    int = 0
    normalised: int = 0
    aligned:    int = 0
    formatted:  int = 0
    stored:     int = 0
    skipped:    int = 0
    errors:     int = 0
    sources:    dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "scraped":    self.scraped,
            "normalised": self.normalised,
            "aligned":    self.aligned,
            "formatted":  self.formatted,
            "stored":     self.stored,
            "skipped":    self.skipped,
            "errors":     self.errors,
            "sources":    self.sources,
            "success_rate": (
                round(self.stored / self.scraped, 3) if self.scraped else 0.0
            ),
        }


# ── Pipeline ──────────────────────────────────────────────────────────────────

class Pipeline:
    """
    Four-stage ingestion pipeline.

    Parameters
    ----------
    db_url:
        SQLAlchemy async database URL.
        Use ``postgresql+asyncpg://`` for production,
        ``sqlite+aiosqlite:///dev.db`` for local dev / tests.
    batch_size:
        How many records to write per DB transaction.
    dry_run:
        If True, run all stages but skip actual DB writes.
    export_jsonl:
        Optional path prefix; if given, training records are also
        written to ``{export_jsonl}_{source_id}.jsonl``.
    """

    def __init__(
        self,
        db_url: str = "sqlite+aiosqlite:///ingestion_dev.db",
        batch_size: int = 200,
        dry_run: bool = False,
        export_jsonl: str | None = None,
        export_format: str = "openai",
    ) -> None:
        self._storage    = StorageLayer(db_url=db_url, batch_size=batch_size)
        self._dry_run    = dry_run
        self._export_dir = export_jsonl
        self._export_format = self._validate_export_format(export_format)
        self._stats      = PipelineStats()
        self._lock       = asyncio.Lock()
        self._raw_buf:    list[RawContent]     = []
        self._norm_buf:   list[NormalisedContent] = []
        self._train_buf:  list[TrainingRecord] = []

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def init(self) -> None:
        """Connect to the database and create tables if they don't exist."""
        if not self._dry_run:
            await self._storage.init()
        logger.info("[Pipeline] Initialised (dry_run=%s)", self._dry_run)

    async def close(self) -> None:
        """Flush remaining batches and close the DB connection."""
        await self._flush()
        if not self._dry_run:
            await self._storage.close()
        logger.info("[Pipeline] Closed — %s", self._stats.as_dict())

    # ── Main processing entry point ───────────────────────────────────────────

    async def process(self, raw: RawContent) -> TrainingRecord | None:
        """
        Run *raw* through all four pipeline stages.

        Returns the resulting :class:`TrainingRecord`, or ``None``
        if the item was filtered out at any stage.
        """
        self._stats.scraped += 1
        self._stats.sources[raw.source_id] = (
            self._stats.sources.get(raw.source_id, 0) + 1
        )

        # ── Stage 1: Normalise ────────────────────────────────────────────────
        try:
            normed = normalise(raw)
        except Exception as exc:
            logger.warning("[Pipeline] Normalise error for %s: %s", raw.source_url, exc)
            self._stats.errors += 1
            return None

        if normed is None:
            self._stats.skipped += 1
            return None
        self._stats.normalised += 1

        # ── Stage 2: CAPS Align ───────────────────────────────────────────────
        try:
            aligned = align(normed)
        except Exception as exc:
            logger.warning("[Pipeline] Align error for %s: %s", normed.source_url, exc)
            aligned = normed   # fall through without alignment
        self._stats.aligned += 1

        # ── Stage 3: Format ───────────────────────────────────────────────────
        try:
            record = format_record(aligned)
        except Exception as exc:
            logger.warning("[Pipeline] Format error for %s: %s", aligned.source_url, exc)
            self._stats.errors += 1
            return None

        if record is None:
            self._stats.skipped += 1
            return None
        self._stats.formatted += 1

        # ── Stage 4: Store ────────────────────────────────────────────────────
        async with self._lock:
            self._raw_buf.append(raw)
            self._norm_buf.append(aligned)
            self._train_buf.append(record)

            if len(self._train_buf) >= self._storage._batch_size:
                await self._flush()

        self._stats.stored += 1
        return record

    # ── Batch processing ──────────────────────────────────────────────────────

    async def process_batch(self, raws: list[RawContent]) -> list[TrainingRecord]:
        """Process many RawContent items concurrently (bounded concurrency)."""
        sem = asyncio.Semaphore(16)

        async def _one(raw: RawContent) -> TrainingRecord | None:
            async with sem:
                return await self.process(raw)

        results = await asyncio.gather(*[_one(r) for r in raws], return_exceptions=True)
        return [r for r in results if isinstance(r, TrainingRecord)]

    # ── Internal ──────────────────────────────────────────────────────────────

    async def _flush(self) -> None:
        """Write buffered records to storage (no-op in dry_run mode)."""
        if not (self._raw_buf or self._norm_buf or self._train_buf):
            return

        if not self._dry_run:
            await self._storage.save_raw_batch(self._raw_buf)
            await self._storage.save_normalised_batch(self._norm_buf)
            await self._storage.save_training_batch(self._train_buf)

        if self._export_dir and self._train_buf:
            await self._write_jsonl(self._train_buf)

        logger.debug(
            "[Pipeline] Flushed %d raw / %d normalised / %d training records",
            len(self._raw_buf), len(self._norm_buf), len(self._train_buf),
        )
        self._raw_buf.clear()
        self._norm_buf.clear()
        self._train_buf.clear()

    async def _write_jsonl(self, records: list[TrainingRecord]) -> None:
        """Append training records to per-source JSONL export files."""
        import json
        from pathlib import Path

        by_source: dict[str, list[TrainingRecord]] = {}
        for rec in records:
            by_source.setdefault(rec.source_id, []).append(rec)

        for source_id, recs in by_source.items():
            path = Path(self._export_dir) / f"{source_id}.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as fh:
                for rec in recs:
                    row = rec.to_anthropic_format() if self._export_format == "anthropic" else rec.to_openai_format()
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    # ── Stats ─────────────────────────────────────────────────────────────────

    def stats(self) -> dict[str, Any]:
        """Return a snapshot of the current pipeline statistics."""
        return self._stats.as_dict()

    @staticmethod
    def _validate_export_format(fmt: str) -> str:
        mode = fmt.lower().strip()
        if mode not in {"openai", "anthropic"}:
            raise ValueError(f"Unsupported export format: {fmt}")
        return mode


# ── Re-exports ────────────────────────────────────────────────────────────────


__all__ = [
    "Pipeline",
    "PipelineStats",
    "StorageLayer",
    "normalise",
    "align",
    "format_record",
]
