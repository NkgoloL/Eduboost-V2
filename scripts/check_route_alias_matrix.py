#!/usr/bin/env python3
"""Enforce /api/v2 -> /v2 route alias policy."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

from scripts.generate_route_alias_matrix import RouteRow, collect_rows, render_markdown


MATRIX_PATH = Path("docs/release/route_alias_matrix.md")
EXCEPTIONS_PATH = Path("docs/release/route_alias_exceptions.txt")


@dataclass(frozen=True)
class AliasException:
    method: str
    canonical_path: str
    reason: str

    @property
    def key(self) -> tuple[str, str]:
        return (self.method.upper(), self.canonical_path)


def parse_exceptions(path: Path = EXCEPTIONS_PATH) -> dict[tuple[str, str], AliasException]:
    if not path.exists():
        return {}

    exceptions: dict[tuple[str, str], AliasException] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        # Format: METHOD /api/v2/path -- reason
        if " -- " not in line:
            raise ValueError(f"Invalid alias exception line, expected 'METHOD /api/v2/path -- reason': {raw_line!r}")
        left, reason = line.split(" -- ", 1)
        parts = left.split(maxsplit=1)
        if len(parts) != 2:
            raise ValueError(f"Invalid alias exception route key: {raw_line!r}")
        method, canonical_path = parts[0].upper(), parts[1]
        if not canonical_path.startswith("/api/v2/"):
            raise ValueError(f"Alias exception must reference canonical /api/v2 route: {raw_line!r}")
        exceptions[(method, canonical_path)] = AliasException(method, canonical_path, reason.strip())
    return exceptions


def missing_alias_rows(rows: list[RouteRow], exceptions: dict[tuple[str, str], AliasException]) -> list[RouteRow]:
    return [
        row
        for row in rows
        if not row.alias_present and (row.method.upper(), row.canonical_path) not in exceptions
    ]


def stale_exceptions(rows: list[RouteRow], exceptions: dict[tuple[str, str], AliasException]) -> list[AliasException]:
    route_keys = {(row.method.upper(), row.canonical_path) for row in rows}
    return [exception for key, exception in exceptions.items() if key not in route_keys]


def write_baseline(rows: list[RouteRow], path: Path = EXCEPTIONS_PATH) -> None:
    missing = [row for row in rows if not row.alias_present]
    lines = [
        "# EduBoost V2 route alias exceptions",
        "# Format: METHOD /api/v2/path -- reason",
        "# This file is a baseline. New exceptions require reviewer approval.",
        "",
    ]
    for row in missing:
        lines.append(f"{row.method.upper()} {row.canonical_path} -- baseline exception; review before release")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-baseline", action="store_true", help="Write current missing alias routes as explicit exceptions.")
    args = parser.parse_args(argv)

    rows = collect_rows()
    MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)
    MATRIX_PATH.write_text(render_markdown(rows), encoding="utf-8")

    if args.write_baseline:
        write_baseline(rows)
        print(f"Wrote {EXCEPTIONS_PATH}")

    try:
        exceptions = parse_exceptions()
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    missing = missing_alias_rows(rows, exceptions)
    stale = stale_exceptions(rows, exceptions)

    print("Route alias policy check")
    print(f"- Matrix: {MATRIX_PATH}")
    print(f"- Canonical /api/v2 rows: {len(rows)}")
    print(f"- Explicit exceptions: {len(exceptions)}")

    if stale:
        print("- WARN stale exceptions:")
        for exception in stale:
            print(f"  - {exception.method} {exception.canonical_path} -- {exception.reason}")

    if missing:
        print("- FAIL missing aliases without exception:", file=sys.stderr)
        for row in missing:
            print(f"  - {row.method} {row.canonical_path} -> {row.alias_path}", file=sys.stderr)
        print("Run `python3 scripts/check_route_alias_matrix.py --write-baseline` only if these exceptions are intentional.", file=sys.stderr)
        return 1

    print("- PASS all missing aliases are explicitly documented")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[1]
for candidate in (REPO_ROOT, SCRIPT_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

