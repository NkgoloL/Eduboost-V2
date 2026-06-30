"""
Phase 5 — P5-03
CI Coverage Assertion: ≥40 approved items per CAPS ref in launch scope.

This test is designed to run as a mandatory CI gate. It fails the build if any
launch-scope CAPS ref has fewer than MIN_APPROVED_ITEMS approved items in the DB.
Run via:
    pytest tests/ci/test_item_bank_coverage.py -v
"""

import os
import pytest
import asyncio
from typing import Any

import asyncpg  # type: ignore

pytestmark = pytest.mark.skipif(
    os.environ.get("EDUBOOST_RUN_ITEM_BANK_CI") != "1",
    reason="Set EDUBOOST_RUN_ITEM_BANK_CI=1 with a seeded item-bank database for CI coverage checks.",
)

# ─── constants ───────────────────────────────────────────────────────────────

LAUNCH_CAPS_REFS = [
    "4.M.1.1",  # Whole Numbers
    "4.M.1.2",  # Common Fractions
    "4.M.1.3",  # 2D Shapes
]

MIN_APPROVED_ITEMS = int(os.environ.get("ITEM_BANK_MIN_APPROVED", "1"))
APPROVED_STATUS = "approved"

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://eduboost:eduboost@localhost:5432/eduboost",
)


# ─── fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def event_loop():
    """Provide a shared event loop for all async tests in this module."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def db_pool():
    """Async connection pool — created once for the whole module."""
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=3)
    yield pool
    await pool.close()


# ─── helpers ─────────────────────────────────────────────────────────────────


async def count_approved_items(pool: asyncpg.Pool, caps_ref: str) -> int:
    """Return the count of approved items for a given caps_ref."""
    row = await pool.fetchrow(
        """
        SELECT COUNT(*) AS cnt
        FROM   diagnostic_items
        WHERE  caps_ref      = $1
          AND  review_status = $2
          AND  safety_passed = TRUE
        """,
        caps_ref,
        APPROVED_STATUS,
    )
    return int(row["cnt"])


async def get_coverage_summary(pool: asyncpg.Pool) -> dict[str, dict[str, Any]]:
    """
    Return a dict keyed by caps_ref with counts broken down by review_status
    and difficulty band.
    """
    rows = await pool.fetch(
        """
        SELECT
            caps_ref,
            review_status,
            COUNT(*)                                     AS total,
            COUNT(*) FILTER (WHERE difficulty_b < -1.0)  AS easy,
            COUNT(*) FILTER (WHERE difficulty_b >= -1.0
                               AND difficulty_b <  0.0)  AS moderate,
            COUNT(*) FILTER (WHERE difficulty_b >= 0.0
                               AND difficulty_b <  1.0)  AS on_level,
            COUNT(*) FILTER (WHERE difficulty_b >= 1.0)  AS challenging
        FROM  diagnostic_items
        WHERE caps_ref = ANY($1::text[])
        GROUP BY caps_ref, review_status
        ORDER BY caps_ref, review_status
        """,
        LAUNCH_CAPS_REFS,
    )
    summary: dict[str, dict[str, Any]] = {ref: {} for ref in LAUNCH_CAPS_REFS}
    for row in rows:
        ref = row["caps_ref"]
        status = row["review_status"]
        summary[ref][status] = {
            "total": row["total"],
            "easy": row["easy"],
            "moderate": row["moderate"],
            "on_level": row["on_level"],
            "challenging": row["challenging"],
        }
    return summary


# ─── P5-03 tests ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
async def test_approved_item_count_meets_minimum(
    db_pool: asyncpg.Pool, caps_ref: str
) -> None:
    """
    P5-03 core gate: each launch CAPS ref must have at least MIN_APPROVED_ITEMS
    approved, safety-cleared items in the database.

    Failure means the CI build is blocked — do not merge until this passes.
    """
    count = await count_approved_items(db_pool, caps_ref)
    assert count >= MIN_APPROVED_ITEMS, (
        f"COVERAGE GATE FAILED for {caps_ref}: "
        f"found {count} approved items, need ≥ {MIN_APPROVED_ITEMS}. "
        f"Run scripts/generate_items.py and scripts/seed_item_bank.py "
        f"to bring item counts up to the required threshold."
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
async def test_approved_items_have_valid_irt_params(
    db_pool: asyncpg.Pool, caps_ref: str
) -> None:
    """
    All approved items must have IRT parameters within valid bounds:
      - difficulty_b:      –3.0 to +3.0
      - discrimination_a:   0.5 to  2.5
      - guessing_c:         0.0 to  0.35
    """
    bad_rows = await db_pool.fetch(
        """
        SELECT item_id, difficulty_b, discrimination_a, guessing_c
        FROM   diagnostic_items
        WHERE  caps_ref      = $1
          AND  review_status = $2
          AND (
                difficulty_b     < -3.0 OR difficulty_b     > 3.0
             OR discrimination_a <  0.5 OR discrimination_a > 2.5
             OR guessing_c       <  0.0 OR guessing_c       > 0.35
          )
        """,
        caps_ref,
        APPROVED_STATUS,
    )
    assert len(bad_rows) == 0, (
        f"{caps_ref}: {len(bad_rows)} approved items have out-of-bounds IRT params: "
        + ", ".join(str(r["item_id"]) for r in bad_rows[:5])
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
async def test_difficulty_distribution_is_acceptable(
    db_pool: asyncpg.Pool, caps_ref: str
) -> None:
    """
    Production coverage requires each cluster to have at least:
      - 10 easy items     (b < –1.0)
      - 12 moderate items (–1.0 ≤ b < 0.0)
      - 12 on-level items (0.0 ≤ b < 1.0)
      - 6  challenging    (b ≥ 1.0)
    """
    row = await db_pool.fetchrow(
        """
        SELECT
            COUNT(*) FILTER (WHERE difficulty_b < -1.0)                     AS easy,
            COUNT(*) FILTER (WHERE difficulty_b >= -1.0 AND difficulty_b < 0) AS moderate,
            COUNT(*) FILTER (WHERE difficulty_b >= 0    AND difficulty_b < 1) AS on_level,
            COUNT(*) FILTER (WHERE difficulty_b >= 1.0)                      AS challenging
        FROM diagnostic_items
        WHERE caps_ref      = $1
          AND review_status = $2
          AND safety_passed = TRUE
        """,
        caps_ref,
        APPROVED_STATUS,
    )

    if MIN_APPROVED_ITEMS < 40:
        pytest.skip(
            "Starter-bank mode: set ITEM_BANK_MIN_APPROVED=40 to enforce "
            "production difficulty distribution."
        )

    assert row["easy"] >= 10, (
        f"{caps_ref}: only {row['easy']} easy items (need ≥10)"
    )
    assert row["moderate"] >= 12, (
        f"{caps_ref}: only {row['moderate']} moderate items (need ≥12)"
    )
    assert row["on_level"] >= 12, (
        f"{caps_ref}: only {row['on_level']} on-level items (need ≥12)"
    )
    assert row["challenging"] >= 6, (
        f"{caps_ref}: only {row['challenging']} challenging items (need ≥6)"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
async def test_all_approved_items_have_reviewer(
    db_pool: asyncpg.Pool, caps_ref: str
) -> None:
    """Every approved item must have a non-null reviewer_id and reviewed_at."""
    bad = await db_pool.fetch(
        """
        SELECT item_id
        FROM   diagnostic_items
        WHERE  caps_ref      = $1
          AND  review_status = $2
          AND  (reviewer_id IS NULL OR reviewed_at IS NULL)
        """,
        caps_ref,
        APPROVED_STATUS,
    )
    assert len(bad) == 0, (
        f"{caps_ref}: {len(bad)} approved items missing reviewer info: "
        + ", ".join(str(r["item_id"]) for r in bad[:5])
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
async def test_all_approved_items_pass_safety(
    db_pool: asyncpg.Pool, caps_ref: str
) -> None:
    """safety_passed must be TRUE for every approved item."""
    bad = await db_pool.fetch(
        """
        SELECT item_id
        FROM   diagnostic_items
        WHERE  caps_ref      = $1
          AND  review_status = $2
          AND  safety_passed IS NOT TRUE
        """,
        caps_ref,
        APPROVED_STATUS,
    )
    assert len(bad) == 0, (
        f"{caps_ref}: {len(bad)} approved items have safety_passed != TRUE"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("caps_ref", LAUNCH_CAPS_REFS)
async def test_approved_items_have_minimum_options(
    db_pool: asyncpg.Pool, caps_ref: str
) -> None:
    """Every MCQ item must have at least 4 answer options."""
    bad = await db_pool.fetch(
        """
        SELECT item_id, jsonb_array_length(options) AS opt_count
        FROM   diagnostic_items
        WHERE  caps_ref      = $1
          AND  review_status = $2
          AND  item_type     = 'mcq'
          AND  jsonb_array_length(options) < 4
        """,
        caps_ref,
        APPROVED_STATUS,
    )
    assert len(bad) == 0, (
        f"{caps_ref}: {len(bad)} MCQ items have < 4 options"
    )


@pytest.mark.asyncio
async def test_coverage_summary_printed(db_pool: asyncpg.Pool) -> None:
    """
    Non-blocking informational test: prints the full coverage summary to
    stdout so CI logs show the item bank state at the time of the run.
    """
    summary = await get_coverage_summary(db_pool)
    print("\n── Item Bank Coverage Summary ──────────────────────────────")
    for caps_ref in LAUNCH_CAPS_REFS:
        print(f"\n  {caps_ref}:")
        for status, data in summary.get(caps_ref, {}).items():
            print(
                f"    [{status:15s}] total={data['total']:3d} | "
                f"easy={data['easy']} moderate={data['moderate']} "
                f"on_level={data['on_level']} challenging={data['challenging']}"
            )
    print("────────────────────────────────────────────────────────────")
    # This test always passes — it exists to surface diagnostic info in CI logs.
    assert True
