#!/usr/bin/env python3
"""
scripts/generate_coverage_matrix.py

Queries the live PostgreSQL database and regenerates
docs/caps/grade4_maths_coverage_matrix.md with current item bank statistics.

Called by:
  - make coverage-matrix          (developer workflow)
  - CI pipeline after seeding     (post-seed verification step)

Usage:
    python scripts/generate_coverage_matrix.py \\
        --output docs/caps/grade4_maths_coverage_matrix.md \\
        --db-url postgresql://eduboost:eduboost@localhost:5432/eduboost
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import asyncpg  # type: ignore
except ImportError:
    print("ERROR: asyncpg not installed. Run: pip install asyncpg", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "caps" / "grade4_maths_coverage_matrix.md"
DEFAULT_DB_URL = "postgresql://eduboost:eduboost@localhost:5432/eduboost"

LAUNCH_CAPS_REFS = {
    "4.M.1.1": "Whole Numbers",
    "4.M.1.2": "Common Fractions",
    "4.M.1.3": "2D Shapes",
}

STATUS_ICON = {True: "✅ READY", False: "⏳ IN PROGRESS"}
IRT_ICON = {True: "✅ Yes", False: "⏳ Pending"}


async def fetch_coverage(pool: asyncpg.Pool) -> dict[str, Any]:
    """Fetch all statistics needed to populate the coverage matrix."""
    data: dict[str, Any] = {}

    for caps_ref in LAUNCH_CAPS_REFS:
        key = caps_ref.replace(".", "")  # e.g. "4M11"

        # Status counts
        rows = await pool.fetch(
            """
            SELECT review_status, COUNT(*) AS cnt
            FROM   diagnostic_items
            WHERE  caps_ref = $1
            GROUP  BY review_status
            """,
            caps_ref,
        )
        status_map = {r["review_status"]: int(r["cnt"]) for r in rows}
        approved = status_map.get("approved", 0)
        draft = status_map.get("draft", 0)
        ai_gen = status_map.get("ai_generated", 0)
        retired = status_map.get("retired", 0)

        data[f"{key}_APPROVED"] = approved
        data[f"{key}_DRAFT"] = draft
        data[f"{key}_AI_GEN"] = ai_gen
        data[f"{key}_RETIRED"] = retired
        data[f"{key}_STATUS"] = STATUS_ICON[approved >= 40]

        # IRT calibration: check if all approved items have non-default a/c params
        irt_calibrated = await pool.fetchval(
            """
            SELECT COUNT(*) = 0
            FROM   diagnostic_items
            WHERE  caps_ref      = $1
              AND  review_status = 'approved'
              AND  (discrimination_a = 1.0 AND guessing_c = 0.25)
            """,
            caps_ref,
        )
        data[f"{key}_IRT"] = IRT_ICON[bool(irt_calibrated)]

        # Difficulty distribution
        diff_row = await pool.fetchrow(
            """
            SELECT
                COUNT(*) FILTER (WHERE difficulty_b < -1.0)                       AS easy,
                COUNT(*) FILTER (WHERE difficulty_b >= -1.0 AND difficulty_b < 0) AS moderate,
                COUNT(*) FILTER (WHERE difficulty_b >= 0    AND difficulty_b < 1) AS on_level,
                COUNT(*) FILTER (WHERE difficulty_b >= 1.0)                       AS challenging
            FROM diagnostic_items
            WHERE caps_ref = $1 AND review_status = 'approved'
            """,
            caps_ref,
        )
        targets = {"easy": 10, "moderate": 12, "on_level": 12, "challenging": 6}
        band_map = {"easy": "EASY", "moderate": "MOD", "on_level": "ONL", "challenging": "CHAL"}
        for band, placeholder in band_map.items():
            actual = int(diff_row[band])
            target = targets[band]
            gap = max(0, target - actual)
            data[f"{key}_{placeholder}"] = actual
            data[f"{key}_{placeholder}_GAP"] = f"**{gap} needed**" if gap > 0 else "✅"

        # Quality scores
        qual_row = await pool.fetchrow(
            """
            SELECT
                ROUND(AVG(quality_score)::numeric, 2) AS mean_q,
                ROUND(MIN(quality_score)::numeric, 2) AS min_q,
                COUNT(*) FILTER (WHERE quality_score < 0.7)  AS low_count
            FROM diagnostic_items
            WHERE caps_ref = $1 AND review_status = 'approved'
              AND quality_score IS NOT NULL
            """,
            caps_ref,
        )
        data[f"{key}_QUAL_MEAN"] = str(qual_row["mean_q"] or "—")
        data[f"{key}_QUAL_MIN"] = str(qual_row["min_q"] or "—")
        low = int(qual_row["low_count"] or 0)
        data[f"{key}_QUAL_LOW"] = f"**{low}** ⚠️" if low > 0 else "0"

        # Reviewer names
        reviewer_row = await pool.fetchrow(
            """
            SELECT STRING_AGG(DISTINCT u.email, ', ') AS reviewers
            FROM   diagnostic_items di
            JOIN   users u ON u.id = di.reviewer_id
            WHERE  di.caps_ref = $1 AND di.review_status = 'approved'
            """,
            caps_ref,
        )
        data[f"{key}_REVIEWER"] = reviewer_row["reviewers"] or "—"

        # Exposure heatmap
        exp_row = await pool.fetchrow(
            """
            SELECT
                COALESCE(SUM(exposure_count), 0) AS total_exp,
                COUNT(*) FILTER (WHERE exposure_count::float / NULLIF(max_exposure,0) >= 0.8) AS exp_80,
                COUNT(*) FILTER (WHERE exposure_count >= max_exposure)                          AS exp_100
            FROM diagnostic_items
            WHERE caps_ref = $1 AND review_status = 'approved'
            """,
            caps_ref,
        )
        total_exp = int(exp_row["total_exp"])
        exp_80 = int(exp_row["exp_80"])
        exp_100 = int(exp_row["exp_100"])
        data[f"{key}_EXP_TOTAL"] = total_exp
        data[f"{key}_EXP_80"] = exp_80
        data[f"{key}_EXP_100"] = exp_100
        replenish_needed = exp_80 > (approved * 0.2)
        data[f"{key}_REPLENISH"] = "⚠️ Yes" if replenish_needed else "✅ No"

        # Misconception tag coverage
        tag_rows = await pool.fetch(
            """
            SELECT tag, COUNT(*) AS cnt
            FROM   diagnostic_items,
                   LATERAL jsonb_array_elements_text(misconception_tags::jsonb) AS tag
            WHERE  caps_ref      = $1
              AND  review_status = 'approved'
            GROUP  BY tag
            ORDER  BY cnt DESC
            """,
            caps_ref,
        )
        for tag_row in tag_rows:
            tag_key = tag_row["tag"].upper().replace("-", "_").replace(" ", "_")
            data[f"{caps_ref.replace('.','_')}_{tag_key}_COUNT"] = int(tag_row["cnt"])

    return data


def replace_placeholders(template: str, data: dict[str, Any], generated_at: str) -> str:
    """Replace all <!-- KEY --> placeholders with data values."""
    result = template.replace("<!-- GENERATED_AT -->", generated_at)
    for key, value in data.items():
        result = result.replace(f"<!-- {key} -->", str(value))
    # Replace any remaining unfilled placeholders with "—"
    result = re.sub(r"<!-- [A-Z0-9_.]+ -->", "—", result)
    return result


async def main(output_path: Path, db_url: str) -> None:
    template_path = output_path  # The file serves as its own template initially
    if not template_path.exists():
        print(
            f"ERROR: Template not found at {template_path}. "
            "Ensure the coverage matrix template is committed first.",
            file=sys.stderr,
        )
        sys.exit(1)

    template = template_path.read_text(encoding="utf-8")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    print("Connecting to database...")
    pool = await asyncpg.create_pool(db_url, min_size=1, max_size=3)
    try:
        print("Fetching item bank statistics...")
        data = await fetch_coverage(pool)
    finally:
        await pool.close()

    print(f"Populating {len(data)} placeholders...")
    output = replace_placeholders(template, data, generated_at)

    output_path.write_text(output, encoding="utf-8")
    print(f"✅ Coverage matrix written to {output_path}")

    # Print summary
    for caps_ref in LAUNCH_CAPS_REFS:
        key = caps_ref.replace(".", "")
        approved = data.get(f"{key}_APPROVED", 0)
        status = data.get(f"{key}_STATUS", "?")
        print(f"   {caps_ref}: {approved} approved  {status}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate CAPS item bank coverage matrix")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output markdown file path",
    )
    parser.add_argument(
        "--db-url",
        default=DEFAULT_DB_URL,
        help="PostgreSQL connection URL",
    )
    args = parser.parse_args()
    asyncio.run(main(args.output, args.db_url))
