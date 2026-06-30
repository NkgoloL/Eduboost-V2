#!/usr/bin/env python3
"""Generate an inventory of audit-related call sites."""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "release" / "audit_callsite_inventory.md"
SCAN_ROOTS = ("app", "tests", "scripts", "alembic")


@dataclass(frozen=True)
class InventoryRow:
    path: str
    line: int
    category: str
    text: str


PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("audit_repository", re.compile(r"\bAuditRepository\b")),
    ("audit_record_call", re.compile(r"\.record\(")),
    ("audit_append_call", re.compile(r"\.append\(")),
    ("audit_events_table", re.compile(r"\baudit_events\b")),
    ("audit_logs_table", re.compile(r"\baudit_logs\b")),
    ("audit_log_identifier", re.compile(r"\bAuditLog\b|\baudit_log\b")),
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
        "# Audit Call-Site Inventory",
        "",
        "This inventory supports audit repository consolidation. It is diagnostic only.",
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
            "- [ ] Confirm canonical append-only audit table.",
            "- [ ] Confirm all security/POPIA-sensitive actions emit canonical audit events.",
            "- [ ] Identify legacy `append` call sites that need adapter migration.",
            "- [ ] Identify any `audit_logs` data-retention requirement.",
            "- [ ] Delete legacy audit code only after adapter migration and full-suite evidence.",
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
        print("No audit call sites found")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
