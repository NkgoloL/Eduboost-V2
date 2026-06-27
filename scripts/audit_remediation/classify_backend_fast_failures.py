#!/usr/bin/env python3
"""Classify backend fast-gate pytest failures for audit-remediation triage."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

CATEGORY_PATTERNS: dict[str, tuple[str, ...]] = {
    "content_factory_registry": (
        r"data/content_factory",
        r"scopes\.json",
        r"coverage_targets\.json",
        r"Content Factory",
    ),
    "popia_auth_or_route_contract": (
        r"AuthContext",
        r"POPIA",
        r"popia",
        r"data-rights",
        r"erasure",
    ),
    "openapi_route_contract": (
        r"OpenAPI",
        r"openapi\.json",
        r"route contract",
        r"schema drift",
    ),
    "database_or_migration": (
        r"sqlalchemy",
        r"alembic",
        r"OperationalError",
        r"ProgrammingError",
        r"migration",
    ),
    "dependency_or_import": (
        r"ModuleNotFoundError",
        r"ImportError",
        r"No module named",
        r"DistributionNotFound",
    ),
    "async_mock_warning": (
        r"RuntimeWarning: coroutine .* was never awaited",
        r"AsyncMock",
    ),
}

FAILED_TEST_RE = re.compile(r"^(FAILED|ERROR)\s+([^\s]+)", re.MULTILINE)
SUMMARY_RE = re.compile(r"(?P<count>\d+)\s+(?P<kind>failed|errors?|passed|skipped|xfailed|xpassed)")


def _summary_counts(text: str) -> dict[str, int]:
    summary: dict[str, int] = {}
    for match in SUMMARY_RE.finditer(text):
        kind = match.group("kind")
        if kind == "error":
            kind = "errors"
        summary[kind] = summary.get(kind, 0) + int(match.group("count"))
    return summary


def _failure_count(summary: dict[str, int], failed_tests: list[str]) -> int:
    count = summary.get("failed", 0) + summary.get("errors", 0)
    if not count and failed_tests:
        count = len(failed_tests)
    return count


def _classify_categories(text: str) -> dict[str, dict[str, Any]]:
    categories: dict[str, dict[str, Any]] = {}
    for category, patterns in CATEGORY_PATTERNS.items():
        snippets: list[str] = []
        for pattern in patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                start = max(0, match.start() - 120)
                end = min(len(text), match.end() + 160)
                snippet = " ".join(text[start:end].split())
                if snippet not in snippets:
                    snippets.append(snippet)
                if len(snippets) >= 5:
                    break
            if len(snippets) >= 5:
                break
        if snippets:
            categories[category] = {"matched": True, "snippets": snippets}
    return categories


def classify_text(text: str) -> dict[str, Any]:
    failed_tests = [match.group(2) for match in FAILED_TEST_RE.finditer(text)]
    summary = _summary_counts(text)
    failure_count = _failure_count(summary, failed_tests)

    # Diagnostic categories are meaningful only for failed authority output.  A
    # green pytest log may still contain benign warning text or package/module
    # names such as ``popia``/``AsyncMock``.  Do not carry those into a passing
    # classification, otherwise the evidence verifier can falsely reject a
    # clean ``make test-fast`` run even when failure_count is zero.
    categories = _classify_categories(text) if failure_count else {}

    return {
        "valid": failure_count == 0,
        "failure_count": failure_count,
        "summary_counts": summary,
        "failed_tests": failed_tests[:100],
        "failed_test_count_detected": len(failed_tests),
        "categories": categories,
        "category_names": sorted(categories),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="pytest output file; reads stdin when omitted")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on-failures", action="store_true")
    args = parser.parse_args()

    if args.input:
        text = args.input.read_text(encoding="utf-8", errors="replace")
    else:
        text = sys.stdin.read()
    result = classify_text(text)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("BACKEND FAST OUTPUT HAS NO DETECTED FAILURES" if result["valid"] else "BACKEND FAST OUTPUT HAS FAILURES")
        print(json.dumps(result, indent=2, sort_keys=True))
    if args.fail_on_failures and not result["valid"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
