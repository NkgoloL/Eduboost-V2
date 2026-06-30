#!/usr/bin/env python3
"""Generate an inventory of consent-related call sites and persistence references."""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "release" / "consent_callsite_inventory.md"
SCAN_ROOTS = ("app", "tests", "scripts", "alembic")


@dataclass(frozen=True)
class InventoryRow:
    path: str
    line: int
    category: str
    text: str


PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("consent_service", re.compile(r"\bConsentService\b")),
    ("consent_records_table", re.compile(r"\bconsent_records\b")),
    ("parental_consents_table", re.compile(r"\bparental_consents\b")),
    ("require_active_consent", re.compile(r"\brequire_active_consent\b")),
    ("consent_grant", re.compile(r"\bgrant\(")),
    ("consent_revoke", re.compile(r"\brevoke\(")),
    ("consent_repository", re.compile(r"\bConsentRepository\b|\bconsent_repo\b")),
    ("parental_consent_model", re.compile(r"\bParentalConsent\b")),
]


def iter_candidate_files() -> list[Path]:
    files: list[Path] = []
    for root_name in SCAN_ROOTS:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".md", ".sql"}:
                files.append(path)
    return sorted(files)


def collect_rows() -> list[InventoryRow]:
    rows: list[InventoryRow] = []
    for path in iter_candidate_files():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(lines, start=1):
            for category, pattern in PATTERNS:
                if pattern.search(line):
                    rows.append(
                        InventoryRow(
                            path=str(path.relative_to(REPO_ROOT)),
                            line=line_number,
                            category=category,
                            text=line.strip()[:220],
                        )
                    )
    return rows


def render_markdown(rows: list[InventoryRow]) -> str:
    output = [
        "# Consent Call-Site Inventory",
        "",
        "This inventory supports consent service/table consolidation. It is diagnostic only.",
        "",
        "| Path | Line | Category | Text |",
        "|---|---:|---|---|",
    ]
    for row in rows:
        text = row.text.replace("|", "\\|")
        output.append(f"| `{row.path}` | {row.line} | {row.category} | `{text}` |")

    output.extend(
        [
            "",
            "## Review checklist",
            "",
            "- [ ] Identify the canonical active-consent runtime service.",
            "- [ ] Identify whether `consent_records` is current state, event history, or both.",
            "- [ ] Identify whether `parental_consents` is current state, relationship consent, or legacy.",
            "- [ ] Confirm POPIA routes keep explicit read/write authorization boundaries.",
            "- [ ] Do not merge/drop consent tables without ADR and data-retention decision.",
            "",
        ]
    )
    return "\n".join(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--fail-empty", action="store_true")
    args = parser.parse_args()

    rows = collect_rows()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown(rows), encoding="utf-8")
    print(f"Wrote {output} ({len(rows)} row(s))")

    if args.fail_empty and not rows:
        print("No consent call sites found")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
