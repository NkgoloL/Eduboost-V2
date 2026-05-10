# tests/performance/test_lesson_generation_perf.py
#
# L5-07 — EduBoost SA Phase 5
# Performance tests:
#   - 10 concurrent lesson generation requests → gateway latency p99 < 5 s
#   - Lesson validator latency p99 < 200 ms
#
# Run with:
#   pytest tests/performance/test_lesson_generation_perf.py -v -s \
#     --performance  (requires the full docker stack to be up)
#
# These tests are gated behind a --performance CLI flag so they do not run
# in the normal unit-test suite. The CI performance job passes this flag.

from __future__ import annotations

import asyncio
import statistics
import time
import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_BASE = "http://localhost:8000"
LEARNER_TOKEN = "dev-learner-token"  # Replace with a real token via fixture

PERF_GENERATION_CONCURRENCY = 10
PERF_GENERATION_P99_THRESHOLD_S = 5.0   # p99 < 5 seconds (L5-07)
PERF_VALIDATOR_P99_THRESHOLD_MS = 200.0  # p99 < 200 ms   (L5-07)
PERF_VALIDATOR_ITERATIONS = 100


# ---------------------------------------------------------------------------
# Pytest CLI flag: --performance
# ---------------------------------------------------------------------------

def pytest_addoption(parser: Any) -> None:
    parser.addoption(
        "--performance",
        action="store_true",
        default=False,
        help="Run performance tests (requires running stack)",
    )


def pytest_collection_modifyitems(config: Any, items: list[Any]) -> None:
    if not config.getoption("--performance", default=False):
        skip = pytest.mark.skip(reason="Pass --performance to run performance tests")
        for item in items:
            if "performance" in item.nodeid:
                item.add_marker(skip)


# ---------------------------------------------------------------------------
# Fixture: valid lesson dict (reused from golden prompts)
# ---------------------------------------------------------------------------

def _make_valid_lesson(caps_ref: str = "4.M.1.1") -> dict[str, Any]:
    return {
        "lesson_id": str(uuid.uuid4()),
        "caps_ref": caps_ref,
        "grade": 4,
        "subject": "Mathematics",
        "term": 1,
        "topic": "Whole Numbers",
        "subtopic": "Ordering and Comparing 4-digit Numbers",
        "learning_objectives": [
            "Learners can compare 4-digit numbers using < and >.",
        ],
        "explanation": (
            "When comparing two 4-digit numbers, start at the thousands column. "
            "If the thousands digits are equal, move to the hundreds column. "
            "Continue until you find different digits."
        ),
        "worked_examples": [
            {
                "question": "Which is greater: 4 301 or 4 031?",
                "step_by_step_solution": (
                    "Step 1: Thousands equal (4 = 4).\n"
                    "Step 2: Hundreds: 3 > 0.\n"
                    "Answer: 4 301 > 4 031."
                ),
                "answer": "4 301",
            },
            {
                "question": "Arrange in order from smallest to largest: 2 100, 2 010, 2 001.",
                "step_by_step_solution": (
                    "Step 1: Thousands all equal (2).\n"
                    "Step 2: Hundreds: 1 > 0.\n"
                    "Step 3: 2 001 < 2 010 < 2 100.\n"
                    "Answer: 2 001, 2 010, 2 100."
                ),
                "answer": "2 001, 2 010, 2 100",
            },
        ],
        "practice_questions": [
            {
                "id": "pq1",
                "question": "Which is smaller: 3 450 or 3 405?",
                "options": {"A": "3 450", "B": "3 405", "C": "Equal", "D": "Cannot tell"},
                "correct_answer": "B",
                "explanation": "Compare hundreds: 4 hundreds vs 0 hundreds — 3 405 is smaller.",
            },
            {
                "id": "pq2",
                "question": "What is the largest 4-digit number using digits 1, 3, 5, 7?",
                "options": {"A": "1 357", "B": "7 531", "C": "5 731", "D": "3 571"},
                "correct_answer": "B",
                "explanation": "Place the largest digit in the thousands column: 7 531.",
            },
            {
                "id": "pq3",
                "question": "Order: 6 002, 6 200, 6 020 from largest to smallest.",
                "options": {
                    "A": "6 002, 6 020, 6 200",
                    "B": "6 200, 6 020, 6 002",
                    "C": "6 020, 6 200, 6 002",
                    "D": "6 200, 6 002, 6 020",
                },
                "correct_answer": "B",
                "explanation": "6 200 > 6 020 > 6 002 by comparing hundreds then tens.",
            },
        ],
        "answer_key": {"pq1": "B", "pq2": "B", "pq3": "B"},
        "remediation_hints": [
            {
                "misconception_tag": "place_value_confusion",
                "hint_text": "Always compare from left to right — thousands first.",
                "example": "4 300 vs 4 030: compare hundreds (3 > 0), so 4 300 is bigger.",
            }
        ],
        "difficulty_level": "on_level",
        "language_level": "Grade 4",
        "safety_classification": "safe",
        "pii_check_passed": True,
        "answer_key_verified": True,
        "quality_score": 0.91,
        "review_status": "approved",
        "reviewer_id": None,
        "reviewed_at": None,
        "prompt_template_version": "lesson_generation_v1",
        "provider": "mock",
        "model_version": "mock-v1",
        "generation_latency_ms": 900,
        "token_usage": {"prompt_tokens": 512, "completion_tokens": 850, "total_tokens": 1362},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# L5-07a: Concurrent lesson generation — gateway latency p99 < 5 s
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_lesson_generation_p99_under_5s() -> None:
    """
    L5-07: Fire 10 concurrent lesson generation requests and assert that the
    p99 response latency is below 5 seconds.
    """
    latencies: list[float] = []

    async def generate_one(client: httpx.AsyncClient, i: int) -> None:
        start = time.perf_counter()
        res = await client.post(
            f"{API_BASE}/api/v2/lessons/generate",
            json={"caps_ref": "4.M.1.1", "difficulty": "on_level"},
            headers={"Authorization": f"Bearer {LEARNER_TOKEN}"},
            timeout=30.0,
        )
        elapsed = time.perf_counter() - start
        latencies.append(elapsed)
        assert res.status_code in (200, 201), (
            f"Request {i} failed: HTTP {res.status_code}"
        )

    async with httpx.AsyncClient() as client:
        await asyncio.gather(*[generate_one(client, i) for i in range(PERF_GENERATION_CONCURRENCY)])

    p99 = _percentile(latencies, 99)
    p50 = _percentile(latencies, 50)

    print(f"\n  Generation latency (n={PERF_GENERATION_CONCURRENCY})")
    print(f"    p50 = {p50 * 1000:.0f} ms")
    print(f"    p99 = {p99 * 1000:.0f} ms  (threshold: {PERF_GENERATION_P99_THRESHOLD_S * 1000:.0f} ms)")

    assert p99 < PERF_GENERATION_P99_THRESHOLD_S, (
        f"p99 generation latency {p99 * 1000:.0f} ms exceeds "
        f"{PERF_GENERATION_P99_THRESHOLD_S * 1000:.0f} ms threshold"
    )


# ---------------------------------------------------------------------------
# L5-07b: Validator latency p99 < 200 ms
# ---------------------------------------------------------------------------

def test_lesson_validator_p99_under_200ms() -> None:
    """
    L5-07: Run the lesson validator 100 times on a valid lesson and assert
    p99 latency is below 200 ms (CPU-only, no I/O).
    """
    try:
        from app.modules.lessons.lesson_validator import LessonValidator
        from app.modules.lessons.caps_topic_map_service import CapsTopicMapService
    except ImportError:
        pytest.skip("App modules not importable — run with correct working directory")

    caps_svc = CapsTopicMapService()
    validator = LessonValidator(caps_topic_map_service=caps_svc)
    lesson = _make_valid_lesson()

    latencies: list[float] = []
    for _ in range(PERF_VALIDATOR_ITERATIONS):
        start = time.perf_counter()
        result = validator.validate(lesson)
        elapsed = time.perf_counter() - start
        latencies.append(elapsed * 1000)  # convert to ms
        assert result.is_valid, f"Validator unexpectedly rejected a valid lesson: {result.failed_rules}"

    p99 = _percentile(latencies, 99)
    p50 = _percentile(latencies, 50)

    print(f"\n  Validator latency (n={PERF_VALIDATOR_ITERATIONS})")
    print(f"    p50 = {p50:.1f} ms")
    print(f"    p99 = {p99:.1f} ms  (threshold: {PERF_VALIDATOR_P99_THRESHOLD_MS:.0f} ms)")

    assert p99 < PERF_VALIDATOR_P99_THRESHOLD_MS, (
        f"p99 validator latency {p99:.1f} ms exceeds "
        f"{PERF_VALIDATOR_P99_THRESHOLD_MS:.0f} ms threshold"
    )


# ---------------------------------------------------------------------------
# L5-07c: Validator latency under realistic validation failures
# ---------------------------------------------------------------------------

def test_validator_failure_path_p99_under_200ms() -> None:
    """
    Even when validation FAILS (e.g. missing answer key), the validator must
    return within p99 < 200 ms — it must not hang or retry on bad data.
    """
    try:
        from app.modules.lessons.lesson_validator import LessonValidator
        from app.modules.lessons.caps_topic_map_service import CapsTopicMapService
    except ImportError:
        pytest.skip("App modules not importable")

    caps_svc = CapsTopicMapService()
    validator = LessonValidator(caps_topic_map_service=caps_svc)
    bad_lesson = _make_valid_lesson()
    bad_lesson["answer_key"] = {}
    bad_lesson["answer_key_verified"] = False

    latencies: list[float] = []
    for _ in range(PERF_VALIDATOR_ITERATIONS):
        start = time.perf_counter()
        validator.validate(bad_lesson)
        latencies.append((time.perf_counter() - start) * 1000)

    p99 = _percentile(latencies, 99)
    assert p99 < PERF_VALIDATOR_P99_THRESHOLD_MS, (
        f"Validator failure path p99={p99:.1f}ms exceeds threshold"
    )


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _percentile(data: list[float], pct: int) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * pct / 100
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[-1]
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])
