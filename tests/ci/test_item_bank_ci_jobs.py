"""
Phase 5 — P5-04 & P5-06

P5-04: CI validation test — runs validate_item_bank.py against the seed JSON.
       Fails CI if any approved item fails schema or validator checks.

P5-06: Performance test — 10 concurrent diagnostic sessions → item selection
       latency < 50ms p99 (DB-backed with proper indexes).

Run with:
    pytest tests/ci/test_item_bank_ci_jobs.py -v -s
"""

from __future__ import annotations

import asyncio
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import asyncpg  # type: ignore
import httpx
import pytest

# ─── constants ───────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]
SEED_JSON_PATH = REPO_ROOT / "data" / "caps" / "grade4_maths_item_bank.json"
VALIDATE_SCRIPT = REPO_ROOT / "scripts" / "validate_item_bank.py"

API_URL = os.environ.get("API_URL", "http://localhost:8000")
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://eduboost:eduboost@localhost:5432/eduboost",
)

LEARNER_ID_TEMPLATE = "perf-test-learner-{index}"
GRADE4_CAPS_REFS = ["4.M.1.1", "4.M.1.2", "4.M.1.3"]

# P5-06 SLO: item selection must be < 50ms at p99
ITEM_SELECTION_P99_THRESHOLD_MS = 50.0
CONCURRENT_SESSIONS = 10
ITEMS_PER_SESSION = 8
MIN_APPROVED_SEED_ITEMS = int(os.environ.get("ITEM_BANK_MIN_APPROVED_TOTAL", "14"))


# ─── fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def db_pool():
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=12)
    yield pool
    await pool.close()


@pytest.fixture(scope="module")
async def api_token() -> str:
    """Obtain a service-account token for performance testing."""
    async with httpx.AsyncClient(base_url=API_URL, timeout=10) as client:
        resp = await client.post(
            "/api/v2/auth/login",
            json={
                "email": os.environ.get("E2E_GUARDIAN_EMAIL", "e2e_guardian@test.eduboost.co.za"),
                "password": os.environ.get("E2E_GUARDIAN_PASSWORD", "E2eGuardian#2026!"),
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


# ─── P5-04: Seed JSON Validation ─────────────────────────────────────────────


class TestCISeedValidation:
    """P5-04: Mandatory CI gate — validate_item_bank.py must pass with 0 errors."""

    def test_seed_json_file_exists(self) -> None:
        assert SEED_JSON_PATH.exists(), (
            f"Seed file not found at {SEED_JSON_PATH}. "
            "Run scripts/generate_items.py and scripts/seed_item_bank.py first."
        )

    def test_seed_json_is_valid_json(self) -> None:
        text = SEED_JSON_PATH.read_text(encoding="utf-8")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            pytest.fail(f"Seed JSON is not valid JSON: {exc}")
        assert isinstance(data, dict), "Seed JSON root must be an object"
        assert "items" in data, "Seed JSON must have an 'items' key"

    def test_seed_json_schema_header_present(self) -> None:
        data = json.loads(SEED_JSON_PATH.read_text(encoding="utf-8"))
        assert "schema_version" in data, "Seed JSON must declare a schema_version"
        assert "generated_at" in data, "Seed JSON must declare generated_at"
        assert data.get("items"), "Seed JSON must include item records"
        assert all(item.get("grade") == 4 for item in data["items"])
        assert all(item.get("subject") == "Mathematics" for item in data["items"])

    def test_seed_json_minimum_item_count(self) -> None:
        data = json.loads(SEED_JSON_PATH.read_text(encoding="utf-8"))
        items = data["items"]
        approved = [i for i in items if i.get("review_status") == "approved"]
        assert len(approved) >= MIN_APPROVED_SEED_ITEMS, (
            f"Seed JSON has only {len(approved)} approved items; "
            f"need ≥{MIN_APPROVED_SEED_ITEMS}. Set ITEM_BANK_MIN_APPROVED_TOTAL=120 "
            "for the production launch gate."
        )

    def test_validate_item_bank_script_passes(self) -> None:
        """
        Run validate_item_bank.py as a subprocess and assert exit code 0.
        This mirrors exactly what the CI YAML job does.
        """
        assert VALIDATE_SCRIPT.exists(), (
            f"Validation script not found at {VALIDATE_SCRIPT}"
        )
        result = subprocess.run(
            [sys.executable, str(VALIDATE_SCRIPT), "--path", str(SEED_JSON_PATH)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        # Print output so CI logs show validator detail on failure
        print("\n── validate_item_bank.py stdout ──")
        print(result.stdout[-4000:] if len(result.stdout) > 4000 else result.stdout)
        if result.returncode != 0:
            print("\n── validate_item_bank.py stderr ──")
            print(result.stderr[-2000:])
        assert result.returncode == 0, (
            "validate_item_bank.py exited with non-zero status. "
            "Fix all validation failures before merging. "
            f"Exit code: {result.returncode}"
        )
        # Verify the summary line confirms 0 failures
        assert (
            "0 failures" in result.stdout
            or "PASS" in result.stdout
            or "Failed:           0" in result.stdout
        ), (
            "Validator output did not confirm 0 failures — check stdout above."
        )

    def test_all_approved_items_pass_local_schema_check(self) -> None:
        """
        Lightweight duplicate of the script check using inline Pydantic validation.
        Provides a faster feedback loop during local development.
        """
        data = json.loads(SEED_JSON_PATH.read_text(encoding="utf-8"))
        required_fields = {
            "item_id", "caps_ref", "grade", "subject", "term", "topic",
            "subtopic", "skill", "stem", "answer_key", "options",
            "explanation", "distractor_rationale", "misconception_tags",
            "item_type", "difficulty_b", "discrimination_a", "guessing_c",
            "language", "review_status", "safety_passed",
        }
        failures: list[str] = []
        for item in data["items"]:
            if item.get("review_status") != "approved":
                continue
            missing = required_fields - item.keys()
            if missing:
                failures.append(f"{item.get('item_id', '?')}: missing {missing}")
            # answer_key must be one of the option labels
            option_labels = {o["label"] for o in item.get("options", [])}
            if item.get("answer_key") not in option_labels:
                failures.append(
                    f"{item.get('item_id', '?')}: answer_key "
                    f"'{item.get('answer_key')}' not in options {option_labels}"
                )

        assert len(failures) == 0, (
            f"{len(failures)} approved items failed schema check:\n"
            + "\n".join(failures[:20])
        )


# ─── P5-06: Performance Test ─────────────────────────────────────────────────


class TestItemSelectionPerformance:
    """
    P5-06: 10 concurrent diagnostic sessions → item selection latency < 50ms p99.
    Items are fetched from PostgreSQL using the indexed query path.
    """

    async def _fetch_next_item_timing(
        self,
        client: httpx.AsyncClient,
        token: str,
        session_id: str,
    ) -> float | None:
        """
        Time a single next-item fetch. Returns latency in ms or None on 204.
        """
        start = time.perf_counter()
        resp = await client.get(
            f"/api/v2/diagnostics/sessions/{session_id}/next-item",
            headers={"Authorization": f"Bearer {token}"},
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        if resp.status_code == 204:
            return None
        assert resp.status_code == 200, f"Unexpected status: {resp.status_code}"
        return elapsed_ms

    async def _run_session(
        self,
        client: httpx.AsyncClient,
        token: str,
        learner_id: str,
    ) -> list[float]:
        """
        Start a diagnostic session and collect item-selection latencies.
        Returns a list of latency measurements in ms.
        """
        # Start session
        resp = await client.post(
            "/api/v2/diagnostics/sessions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "learner_id": learner_id,
                "grade": 4,
                "subject": "Mathematics",
                "caps_refs": GRADE4_CAPS_REFS,
            },
        )
        assert resp.status_code == 201, f"Session start failed: {resp.status_code}"
        session_id = resp.json()["session_id"]

        latencies: list[float] = []
        for _ in range(ITEMS_PER_SESSION):
            lat = await self._fetch_next_item_timing(client, token, session_id)
            if lat is None:
                break
            latencies.append(lat)

            # Submit a dummy answer to advance the session
            item_id = (
                await client.get(
                    f"/api/v2/diagnostics/sessions/{session_id}/next-item",
                    headers={"Authorization": f"Bearer {token}"},
                )
            ).json().get("item_id", "")
            if item_id:
                await client.post(
                    f"/api/v2/diagnostics/sessions/{session_id}/responses",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"item_id": item_id, "answer": "A", "response_time_ms": 500},
                )

        # Complete session
        await client.post(
            f"/api/v2/diagnostics/sessions/{session_id}/complete",
            headers={"Authorization": f"Bearer {token}"},
        )
        return latencies

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_item_selection_p99_under_50ms(self, api_token: str) -> None:
        """
        Fire CONCURRENT_SESSIONS sessions simultaneously and collect all
        next-item latencies. p99 must be < ITEM_SELECTION_P99_THRESHOLD_MS.
        """
        async with httpx.AsyncClient(
            base_url=API_URL, timeout=httpx.Timeout(30.0)
        ) as client:
            tasks = [
                self._run_session(
                    client,
                    api_token,
                    LEARNER_ID_TEMPLATE.format(index=i),
                )
                for i in range(CONCURRENT_SESSIONS)
            ]
            all_session_latencies = await asyncio.gather(*tasks)

        # Flatten all latency measurements across all sessions
        all_latencies: list[float] = [
            lat
            for session_lats in all_session_latencies
            for lat in session_lats
        ]

        assert len(all_latencies) > 0, "No latency measurements collected"

        sorted_lats = sorted(all_latencies)
        p50 = sorted_lats[int(len(sorted_lats) * 0.50)]
        p95 = sorted_lats[int(len(sorted_lats) * 0.95)]
        p99_idx = int(len(sorted_lats) * 0.99)
        p99 = sorted_lats[min(p99_idx, len(sorted_lats) - 1)]
        mean = statistics.mean(sorted_lats)
        max_lat = max(sorted_lats)

        print(
            f"\n── Item Selection Latency ({len(all_latencies)} measurements, "
            f"{CONCURRENT_SESSIONS} concurrent sessions) ──\n"
            f"  mean={mean:.1f}ms  p50={p50:.1f}ms  "
            f"p95={p95:.1f}ms  p99={p99:.1f}ms  max={max_lat:.1f}ms\n"
            f"  SLO threshold (p99): < {ITEM_SELECTION_P99_THRESHOLD_MS}ms"
        )

        assert p99 < ITEM_SELECTION_P99_THRESHOLD_MS, (
            f"PERFORMANCE SLO BREACH: item selection p99={p99:.1f}ms exceeds "
            f"{ITEM_SELECTION_P99_THRESHOLD_MS}ms threshold. "
            "Check DB indexes on diagnostic_items (caps_ref, review_status, exposure_count). "
            "Run EXPLAIN ANALYZE on the item selection query."
        )

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_db_index_utilisation(self, db_pool: asyncpg.Pool) -> None:
        """
        Verify that the item selection query uses the expected index via EXPLAIN.
        The query planner must use an Index Scan, not a Seq Scan.
        """
        plan = await db_pool.fetchval(
            """
            EXPLAIN (FORMAT JSON, ANALYZE FALSE)
            SELECT item_id, stem, options, difficulty_b, discrimination_a, guessing_c
            FROM   diagnostic_items
            WHERE  caps_ref      = '4.M.1.1'
              AND  review_status = 'approved'
              AND  safety_passed = TRUE
              AND  exposure_count < max_exposure
            ORDER BY ABS(difficulty_b - 0.0)
            LIMIT 20
            """
        )
        plan_text = json.dumps(plan)
        assert "Index" in plan_text or "Bitmap" in plan_text, (
            "Query planner is using a Sequential Scan for item selection. "
            "Ensure the index idx_diagnostic_items_caps_status exists. "
            f"EXPLAIN output: {plan_text[:500]}"
        )
