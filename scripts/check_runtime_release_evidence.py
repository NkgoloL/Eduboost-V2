#!/usr/bin/env python3
"""Check that runtime/staging release evidence placeholders exist and remain honest."""
from __future__ import annotations

from pathlib import Path


REQUIRED_FILES = [
    Path("docs/release/EVIDENCE_INDEX.md"),
    Path("docs/release/ci_evidence.md"),
    Path("docs/release/staging_smoke_evidence.md"),
    Path("docs/release/migration_evidence.md"),
    Path("docs/release/restore_drill_evidence.md"),
    Path("docs/release/rollback_drill_evidence.md"),
    Path("docs/release/final_go_no_go_evidence.md"),
]


def _contains_status(text: str, marker: str) -> bool:
    """Return true for plain, bold Markdown, or comment status markers."""
    bold = marker.replace("Status:", "**Status:**")
    comment = f"<!-- {marker} -->"
    return marker in text or bold in text or comment in text


REQUIRED_CONTENT = {
    Path("docs/release/staging_smoke_evidence.md"): [
        "Status: pending runtime execution",
        "GET /api/v2/health/deep",
        "Auth register/login/refresh/logout",
        "POPIA data export route",
    ],
    Path("docs/release/migration_evidence.md"): [
        "Status: pending runtime execution",
        "alembic upgrade head",
        "schema integrity check",
        "migration graph check",
    ],
    Path("docs/release/restore_drill_evidence.md"): [
        "Status: pending runtime execution",
        "Backup checksum",
        "Restore command completed",
        "application smoke after restore",
    ],
    Path("docs/release/rollback_drill_evidence.md"): [
        "Status: pending runtime execution",
        "Application rollback command",
        "Post-rollback health",
    ],
    Path("docs/release/ci_evidence.md"): [
        "Status: pending remote CI verification",
        "GitHub Actions run URL",
        "Route alias policy",
    ],
    Path("docs/release/final_go_no_go_evidence.md"): [
        "Status: not ready for signoff",
        "GO",
        "NO-GO",
        "CONDITIONAL GO",
    ],
}


def main() -> int:
    failures: list[str] = []
    print("Runtime release evidence check")

    for path in REQUIRED_FILES:
        if path.exists():
            print(f"- PASS [file] {path}: present")
        else:
            print(f"- FAIL [file] {path}: missing")
            failures.append(f"missing file {path}")

    for path, needles in REQUIRED_CONTENT.items():
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for needle in needles:
            matched = _contains_status(text, needle) if needle.startswith("Status:") else needle in text
            if matched:
                print(f"- PASS [content] {path}: contains {needle!r}")
            else:
                print(f"- FAIL [content] {path}: missing {needle!r}")
                failures.append(f"{path} missing {needle!r}")

    pending_files = [
        Path("docs/release/staging_smoke_evidence.md"),
        Path("docs/release/migration_evidence.md"),
        Path("docs/release/restore_drill_evidence.md"),
        Path("docs/release/rollback_drill_evidence.md"),
    ]
    for path in pending_files:
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        if not _contains_status(text, "Status: pending runtime execution"):
            print(f"- FAIL [honesty] {path}: pending status removed before evidence replacement")
            failures.append(f"{path} pending status removed")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
