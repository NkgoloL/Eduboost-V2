#!/usr/bin/env python3
"""Generate a /api/v2 to /v2 route alias matrix from the FastAPI app."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class RouteRow:
    method: str
    canonical_path: str
    alias_path: str
    alias_present: bool
    note: str


def _load_routes() -> set[tuple[str, str]]:
    from app.api_v2 import app

    rows: set[tuple[str, str]] = set()
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", None) or set()
        for method in methods:
            if method in {"HEAD", "OPTIONS"}:
                continue
            rows.add((method, path))
    return rows


def collect_rows(routes: set[tuple[str, str]] | None = None) -> list[RouteRow]:
    route_set = routes if routes is not None else _load_routes()
    canonical = sorted((method, path) for method, path in route_set if path.startswith("/api/v2/"))
    rows: list[RouteRow] = []

    for method, path in canonical:
        alias = "/v2/" + path.removeprefix("/api/v2/")
        alias_present = (method, alias) in route_set
        rows.append(
            RouteRow(
                method=method,
                canonical_path=path,
                alias_path=alias,
                alias_present=alias_present,
                note="compatibility alias present" if alias_present else "no /v2 alias; document if intentional",
            )
        )

    return rows


def render_markdown(rows: Iterable[RouteRow]) -> str:
    rendered = [
        "# EduBoost V2 Route Alias Matrix",
        "",
        "`/api/v2` is canonical. `/v2` is a compatibility alias where present.",
        "",
        "| Method | Canonical route | Compatibility alias | Status | Note |",
        "|---|---|---|---|---|",
    ]

    for row in rows:
        status = "present" if row.alias_present else "missing"
        rendered.append(f"| {row.method} | `{row.canonical_path}` | `{row.alias_path}` | {status} | {row.note} |")

    rendered.append("")
    return "\n".join(rendered)


def main() -> int:
    rows = collect_rows()
    output_path = Path("docs/release/route_alias_matrix.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(rows), encoding="utf-8")

    missing = [row for row in rows if not row.alias_present]
    print(f"Wrote {output_path} ({len(rows)} canonical route(s), {len(missing)} missing alias row(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
