#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from app.services.deep_readiness_readonly import DEFAULT_READINESS_SPECS, assert_read_only_operation, summarize_specs


REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failures: list[str] = []
    print("Deep-readiness read-only guard")

    summary = summarize_specs(DEFAULT_READINESS_SPECS)
    if summary["read_only"] and summary["total"] >= 5:
        print(f"- PASS [specs] {summary['total']} read-only readiness specs")
    else:
        print(f"- FAIL [specs] invalid readiness spec summary: {summary}")
        failures.append("invalid readiness spec summary")

    for bad in ["session.commit()", "INSERT INTO audit_events", "alembic stamp head"]:
        try:
            assert_read_only_operation(bad)
        except ValueError:
            print(f"- PASS [guard] rejected {bad!r}")
        else:
            print(f"- FAIL [guard] accepted write-like operation {bad!r}")
            failures.append(f"accepted {bad!r}")

    contract = REPO_ROOT / "docs/release/deep_readiness_implementation_checklist.md"
    if contract.exists():
        text = contract.read_text(encoding="utf-8")
        if "read-only" in text and "internal/admin only" in text:
            print("- PASS [contract] deep readiness checklist present")
        else:
            print("- FAIL [contract] deep readiness checklist lacks required guardrails")
            failures.append("deep readiness checklist lacks guardrails")
    else:
        print("- WARN [contract] deep readiness checklist not found")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS deep-readiness read-only guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
