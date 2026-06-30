"""
EduBoost SA — Ingestion System Entry Point
==========================================
Orchestrates the full pipeline for one or more sources:

    Scrape → Normalise → CAPS Align → Format → Store

Usage (Python API)::

    from scripts.ingestion.main import run_ingestion

    stats = await run_ingestion(
        source_ids=["siyavula", "dbe"],
        grade_range=(10, 12),
        db_url="postgresql+asyncpg://user:pass@localhost/eduboost",
    )

Usage (CLI)::

    # Run a specific source
    python -m scripts.ingestion.main run --sources khan_academy --grades 7-9 --limit 1000

    # Run all South African sources
    python -m scripts.ingestion.main run --sources za --grades 10-12

    # Dry-run to see what would be scraped
    python -m scripts.ingestion.main run --sources siyavula --dry-run

    # List all available sources
    python -m scripts.ingestion.main sources

    # Show queue status
    python -m scripts.ingestion.main status
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any

import typer

from scripts.ingestion.config import SOURCES, HF_DATASETS
from scripts.ingestion.models import IngestionProgress, JobStatus
from scripts.ingestion.pipeline import Pipeline
from scripts.ingestion.queue_manager import QueueManager
from scripts.ingestion.sources import (
    SCRAPER_REGISTRY,
    ZA_SOURCES,
    OPEN_SOURCES,
    get_scraper,
)

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Typer CLI app ─────────────────────────────────────────────────────────────

app = typer.Typer(
    name="ingestion",
    help="EduBoost SA curriculum ingestion CLI — scrape, normalise, CAPS-align, store.",
    add_completion=False,
)


# ── Core coroutine (importable by API / tests) ────────────────────────────────

async def run_ingestion(
    source_ids: list[str] | None = None,
    grade_range: tuple[int, int] = (1, 12),
    limit: int = 0,
    db_url: str | None = None,
    redis_url: str = "redis://localhost:6379",
    export_dir: str | None = None,
    export_format: str = "openai",
    dry_run: bool = False,
    job_id: str | None = None,
) -> dict[str, Any]:
    """
    Run the full ingestion pipeline for the specified sources.

    Parameters
    ----------
    source_ids:
        List of source IDs (from ``config.SOURCES``).
        Use the aliases ``"za"`` for ZA sources and ``"open"`` for
        global open-licensed sources.
        Defaults to all registered sources.
    grade_range:
        ``(min_grade, max_grade)`` inclusive filter.
    limit:
        Maximum items to scrape per source (0 = unlimited).
    db_url:
        SQLAlchemy async DB URL. Falls back to ``DATABASE_URL`` env var,
        then ``sqlite+aiosqlite:///ingestion_dev.db``.
    redis_url:
        Redis URL for progress reporting.
    export_dir:
        If given, training records are also written as JSONL files here.
    dry_run:
        Run all stages but skip DB writes and JSONL export.
    job_id:
        External job ID (for queue-driven runs). Auto-generated if None.

    Returns
    -------
    dict
        Aggregated pipeline statistics across all sources.
    """
    db_url = db_url or os.environ.get(
        "DATABASE_URL", "sqlite+aiosqlite:///ingestion_dev.db"
    )

    # Resolve source aliases
    resolved_ids = _resolve_source_ids(source_ids)
    if not resolved_ids:
        logger.error("No valid source IDs provided.")
        return {"error": "no_sources"}

    logger.info(
        "Starting ingestion — sources=%s grades=%s limit=%s dry_run=%s",
        resolved_ids, grade_range, limit or "∞", dry_run,
    )

    # ── Init pipeline ─────────────────────────────────────────────────────────
    pipeline = Pipeline(
        db_url=db_url,
        dry_run=dry_run,
        export_jsonl=export_dir,
        export_format=export_format,
    )
    await pipeline.init()

    # ── Optional: connect to Redis for progress reporting ─────────────────────
    qm: QueueManager | None = None
    try:
        qm = QueueManager(redis_url=redis_url)
        await qm.connect()
    except Exception:
        logger.warning("Redis unavailable — progress reporting disabled")
        qm = None

    overall_start = time.monotonic()
    all_stats: dict[str, Any] = {}

    # ── Scrape each source sequentially ───────────────────────────────────────
    for source_id in resolved_ids:
        if qm and job_id and await qm.is_cancelled(job_id):
            logger.info("Job %s cancelled — stopping ingestion", job_id)
            break

        logger.info("── Source: %s", source_id)
        source_start = time.monotonic()
        source_count = 0

        try:
            scraper = get_scraper(
                source_id,
                grade_range=grade_range,
                limit=limit,
                progress_cb=_make_progress_cb(source_id, job_id, qm),
            )

            async with scraper:
                async for raw_item in scraper.scrape():
                    if qm and job_id and await qm.is_cancelled(job_id):
                        logger.info("Cancellation detected mid-scrape — stopping")
                        break

                    result = await pipeline.process(raw_item)
                    if result:
                        source_count += 1

        except Exception as exc:
            logger.exception("Fatal error scraping %s: %s", source_id, exc)
            all_stats[source_id] = {"error": str(exc)}
            continue

        elapsed = time.monotonic() - source_start
        per_sec = source_count / elapsed if elapsed else 0
        all_stats[source_id] = {
            "stored": source_count,
            "elapsed_secs": round(elapsed, 1),
            "per_sec": round(per_sec, 2),
        }
        logger.info(
            "── %s done: %d records in %.1fs (%.1f/s)",
            source_id, source_count, elapsed, per_sec,
        )

    # ── Finalize ──────────────────────────────────────────────────────────────
    await pipeline.close()
    if qm:
        await qm.disconnect()

    total_elapsed = time.monotonic() - overall_start
    pipeline_stats = pipeline.stats()
    pipeline_stats["elapsed_secs"] = round(total_elapsed, 1)
    pipeline_stats["per_source"] = all_stats

    logger.info("Ingestion complete in %.1fs — %s", total_elapsed, pipeline_stats)
    return pipeline_stats


# ── CLI Commands ──────────────────────────────────────────────────────────────

@app.command()
def run(
    sources: str = typer.Option(
        "all",
        "--sources", "-s",
        help=(
            "Comma-separated source IDs, or the aliases 'all', 'za', 'open'. "
            "E.g. --sources siyavula,dbe,khan_academy"
        ),
    ),
    grades: str = typer.Option(
        "1-12",
        "--grades", "-g",
        help="Grade range as 'min-max'. E.g. --grades 7-12",
    ),
    limit: int = typer.Option(
        0,
        "--limit", "-l",
        help="Max items per source (0 = unlimited)",
    ),
    db_url: str = typer.Option(
        "",
        "--db",
        help="SQLAlchemy async DB URL (falls back to DATABASE_URL env var)",
    ),
    redis_url: str = typer.Option(
        "redis://localhost:6379",
        "--redis",
        help="Redis URL for progress reporting",
    ),
    export_dir: str = typer.Option(
        "",
        "--export",
        help="Directory to write training JSONL files",
    ),
    export_format: str = typer.Option(
        "openai",
        "--export-format",
        help="JSONL export format: openai or anthropic",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Parse and normalise content but skip all writes",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Run the ingestion pipeline for one or more sources."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    source_ids = None if sources in ("all",) else [s.strip() for s in sources.split(",")]

    lo, hi = _parse_grades(grades)

    stats = asyncio.run(
        run_ingestion(
            source_ids=source_ids,
            grade_range=(lo, hi),
            limit=limit,
            db_url=db_url or None,
            redis_url=redis_url,
            export_dir=export_dir or None,
            export_format=export_format,
            dry_run=dry_run,
        )
    )

    typer.echo("\n── Pipeline Statistics ──")
    import json
    typer.echo(json.dumps(stats, indent=2))

    if stats.get("stored", 0) == 0 and not dry_run:
        raise typer.Exit(code=1)


@app.command(name="sources")
def list_sources() -> None:
    """List all available scraper sources."""
    from scripts.ingestion.sources import list_sources as _ls

    typer.echo("\n── Available Sources ──")
    for src_id in _ls():
        cfg = SOURCES.get(src_id)
        if cfg:
            typer.echo(
                f"  {src_id:<30} {cfg.jurisdiction:<8} "
                f"grades {cfg.grade_range[0]}-{cfg.grade_range[1]}  "
                f"{cfg.license}"
            )
        else:
            typer.echo(f"  {src_id}")


@app.command()
def status(
    redis_url: str = typer.Option("redis://localhost:6379", "--redis"),
) -> None:
    """Show the current queue depth and recent job statuses."""

    async def _status() -> None:
        try:
            qm = QueueManager(redis_url=redis_url)
            await qm.connect()
            length = await qm.queue_length()
            jobs   = await qm.peek_queue(n=5)
            await qm.disconnect()
            typer.echo(f"\nQueue depth: {length}")
            if jobs:
                typer.echo("Next jobs:")
                for j in jobs:
                    typer.echo(f"  {j.get('id','')} — source={j.get('source_id')}")
        except Exception as exc:
            typer.echo(f"Cannot connect to Redis: {exc}", err=True)

    asyncio.run(_status())


@app.command()
def datasets() -> None:
    """List all HuggingFace datasets in the catalogue."""
    typer.echo("\n── HuggingFace Dataset Catalogue ──")
    for ds in HF_DATASETS:
        grades = f"{ds['grade_range'][0]}–{ds['grade_range'][1]}"
        typer.echo(f"  {ds['id']:<20} {ds['hf_id']:<45} grades {grades}  {ds['license']}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resolve_source_ids(source_ids: list[str] | None) -> list[str]:
    """Expand aliases and validate IDs."""
    if source_ids is None:
        return list(SCRAPER_REGISTRY.keys())

    resolved: list[str] = []
    for sid in source_ids:
        if sid == "za":
            resolved.extend(ZA_SOURCES)
        elif sid == "open":
            resolved.extend(OPEN_SOURCES)
        elif sid in SCRAPER_REGISTRY:
            resolved.append(sid)
        else:
            logger.warning("Unknown source ID '%s' — skipping", sid)

    # deduplicate preserving order
    seen: set[str] = set()
    return [s for s in resolved if not (s in seen or seen.add(s))]  # type: ignore[func-returns-value]


def _parse_grades(grades: str) -> tuple[int, int]:
    """Parse '7-12' → (7, 12)."""
    try:
        lo_s, hi_s = grades.split("-")
        return int(lo_s), int(hi_s)
    except ValueError:
        typer.echo(f"Invalid grades format '{grades}' — expected 'min-max'", err=True)
        raise typer.Exit(1)


def _make_progress_cb(source_id: str, job_id: str | None, qm: QueueManager | None):
    """Return an async-safe progress callback for the scraper."""
    if not qm or not job_id:
        return None   # scraper will just track internally

    def cb(done: int, total: int, message: str) -> None:
        pct = (done / total * 100) if total else 0.0
        progress = IngestionProgress(
            job_id=job_id,
            source_id=source_id,
            status=JobStatus.RUNNING,
            pct=round(pct, 1),
            scraped=done,
            processed=done,
            message=message,
        )
        # Fire-and-forget into the event loop; scraper calls this synchronously
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(qm.update_progress(progress))
        except RuntimeError:
            pass  # No running loop — skip progress update

    return cb


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()
