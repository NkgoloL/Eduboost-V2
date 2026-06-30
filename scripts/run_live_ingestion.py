#!/usr/bin/env python3
"""
Live Data Ingestion Monitor
============================
Real-time pipeline execution with quality monitoring.

Tracks:
  • Items scraped, normalized, aligned, stored
  • Grade/subject distribution
  • CAPS alignment confidence
  • Processing time per stage
  • Error rates
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

from scripts.ingestion.config import SOURCES
from scripts.ingestion.main import run_ingestion

# Load environment variables
load_dotenv()

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class IngestionMonitor:
    """Real-time pipeline metrics."""

    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = {
            "scraped": 0,
            "normalized": 0,
            "aligned": 0,
            "stored": 0,
            "failed": 0,
            "grades": {},
            "subjects": {},
            "content_types": {},
            "caps_phases": {},
            "confidence_scores": [],
        }

    def log_metric(self, **data):
        """Update metrics from pipeline output."""
        if "grade" in data:
            g = data["grade"]
            self.metrics["grades"][g] = self.metrics["grades"].get(g, 0) + 1

        if "subject" in data:
            s = data["subject"]
            self.metrics["subjects"][s] = self.metrics["subjects"].get(s, 0) + 1

        if "content_type" in data:
            ct = data["content_type"]
            self.metrics["content_types"][ct] = self.metrics["content_types"].get(ct, 0) + 1

        if "caps_phase" in data:
            cp = data["caps_phase"]
            self.metrics["caps_phases"][cp] = self.metrics["caps_phases"].get(cp, 0) + 1

        if "confidence" in data:
            self.metrics["confidence_scores"].append(data["confidence"])

    def print_summary(self):
        """Print real-time summary."""
        elapsed = (datetime.now() - self.start_time).total_seconds()

        print("\n" + "="*80)
        print("INGESTION MONITOR — REAL-TIME METRICS")
        print("="*80)

        print(f"\nElapsed time: {elapsed:.1f}s")
        print("\nPipeline Progress:")
        print(f"  Scraped:     {self.metrics['scraped']:6d}")
        print(f"  Normalized:  {self.metrics['normalized']:6d}")
        print(f"  Aligned:     {self.metrics['aligned']:6d}")
        print(f"  Stored:      {self.metrics['stored']:6d}")
        print(f"  Failed:      {self.metrics['failed']:6d}")

        if self.metrics["confidence_scores"]:
            avg_conf = sum(self.metrics["confidence_scores"]) / len(self.metrics["confidence_scores"])
            print("\nAlignment Confidence:")
            print(f"  Average: {avg_conf:.2f}")
            print(f"  Min:     {min(self.metrics['confidence_scores']):.2f}")
            print(f"  Max:     {max(self.metrics['confidence_scores']):.2f}")

        if self.metrics["grades"]:
            print("\nGrades Distribution:")
            for grade in sorted(self.metrics["grades"].keys()):
                count = self.metrics["grades"][grade]
                print(f"  Grade {grade:2d}: {count:4d} items")

        if self.metrics["subjects"]:
            print("\nSubjects Distribution:")
            for subj in sorted(self.metrics["subjects"].keys(), key=lambda s: self.metrics["subjects"][s], reverse=True):
                count = self.metrics["subjects"][subj]
                print(f"  {subj:30s}: {count:4d} items")

        if self.metrics["content_types"]:
            print("\nContent Types Distribution:")
            for ctype in sorted(self.metrics["content_types"].keys(), key=lambda ct: self.metrics["content_types"][ct], reverse=True):
                count = self.metrics["content_types"][ctype]
                print(f"  {ctype:30s}: {count:4d} items")

        if self.metrics["caps_phases"]:
            print("\nCAPS Phases Distribution:")
            for phase in sorted(self.metrics["caps_phases"].keys(), key=lambda p: self.metrics["caps_phases"][p], reverse=True):
                count = self.metrics["caps_phases"][phase]
                print(f"  {phase:30s}: {count:4d} items")

        print("\n" + "="*80)


async def run_live_ingestion(
    sources: list[str] | None = None,
    grades: tuple[int, int] = (7, 12),
    limit: int = 50,
    dry_run: bool = False,
    db_url: str | None = None,
):
    """
    Run live ingestion with monitoring.
    
    Parameters
    ----------
    sources:
        Source IDs to ingest. Defaults to South African sources (highest priority).
    grades:
        Grade range to filter.
    limit:
        Max items per source.
    dry_run:
        If True, run all stages but skip DB writes.
    db_url:
        Database URL. Falls back to DATABASE_URL env var.
    """
    if sources is None:
        sources = ["siyavula"]  # Start with Siyavula (CAPS-aligned, high quality)

    # Get database URL from env if not provided
    if db_url is None:
        db_url = os.environ.get("DATABASE_URL")
        if db_url is None:
            logger.error("DATABASE_URL not set. Set it in .env or pass --db-url")
            raise ValueError("DATABASE_URL environment variable not set")

    print("\n" + "▓"*80)
    print("█ EDUBOOST SA — LIVE DATA INGESTION")
    print("▓"*80)

    print("\nConfiguration:")
    print(f"  Sources:  {', '.join(sources)}")
    print(f"  Grades:   {grades[0]}–{grades[1]}")
    print(f"  Limit:    {limit} items per source")
    print(f"  Dry-run:  {dry_run}")
    print(f"  Database: {db_url.split('@')[1] if '@' in db_url else 'unknown'}")
    print(f"  Time:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    monitor = IngestionMonitor()

    try:
        logger.info(
            "Starting live ingestion: sources=%s grades=%s limit=%s dry_run=%s db=%s",
            sources, grades, limit, dry_run, db_url[:30] + "..." if len(db_url) > 30 else db_url,
        )

        # Run the pipeline
        stats = await run_ingestion(
            source_ids=sources,
            grade_range=grades,
            limit=limit,
            dry_run=dry_run,
            db_url=db_url,
        )

        # Parse and display results
        print("\n" + "="*80)
        print("INGESTION RESULTS")
        print("="*80)

        if isinstance(stats, dict):
            print(f"\nRaw stats from pipeline: {json.dumps(stats, indent=2, default=str)}")

            # Try to extract metrics
            if "total_items" in stats:
                print(f"\n  Total items processed: {stats['total_items']}")
            if "errors" in stats:
                print(f"  Errors: {stats['errors']}")

        monitor.print_summary()

        return True

    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        monitor.print_summary()
        return False


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run live data ingestion with monitoring"
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        default=["siyavula"],
        help="Source IDs to ingest (default: siyavula)",
    )
    parser.add_argument(
        "--min-grade",
        type=int,
        default=7,
        help="Minimum grade (default: 7)",
    )
    parser.add_argument(
        "--max-grade",
        type=int,
        default=12,
        help="Maximum grade (default: 12)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max items per source (default: 50)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without writing to DB",
    )
    parser.add_argument(
        "--all-sources",
        action="store_true",
        help="Run all 10 sources (ignores --sources)",
    )
    parser.add_argument(
        "--db-url",
        default=None,
        help="PostgreSQL database URL (falls back to DATABASE_URL env var)",
    )

    args = parser.parse_args()

    sources = args.sources
    if args.all_sources:
        sources = list(SOURCES.keys())
        print(f"[INFO] Running all sources: {', '.join(sources)}")

    success = await run_live_ingestion(
        sources=sources,
        grades=(args.min_grade, args.max_grade),
        limit=args.limit,
        dry_run=args.dry_run,
        db_url=args.db_url,
    )

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
