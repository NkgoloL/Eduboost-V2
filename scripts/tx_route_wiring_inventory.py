from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/architecture/tx_route_wiring_inventory.json"
OUT_MD = ROOT / "docs/architecture/tx_route_wiring_inventory.md"

ROUTE_FILES = {
    "auth": ROOT / "app/api_v2_routers/auth.py",
    "popia": ROOT / "app/api_v2_routers/popia.py",
    "diagnostics": ROOT / "app/api_v2_routers/diagnostics.py",
    "lessons": ROOT / "app/api_v2_routers/lessons.py",
}

TRANSACTIONAL_SERVICE_MARKERS = {
    "auth": ["TransactionalAuthRegistrationService", "auth_transactional_registration"],
    "popia": ["TransactionalPOPIAConsentLifecycleService", "popia_transactional_lifecycle"],
    "diagnostics": ["TransactionalDiagnosticResponseService", "diagnostic_transactional_response"],
    "lessons": ["TransactionalLessonCompletionService", "lesson_transactional_completion"],
}

MUTATION_HINTS = {
    "auth": ["register", "create_dev_session", "dev_session"],
    "popia": ["consent", "grant", "deny", "withdraw", "renew"],
    "diagnostics": ["submit", "respond", "response", "mastery"],
    "lessons": ["complete", "sync", "feedback"],
}


@dataclass(frozen=True)
class RouteFunctionWiring:
    domain: str
    path: str
    function_name: str
    line: int
    is_route: bool
    mutation_candidate: bool
    transactional_marker_present: bool
    status: str


@dataclass(frozen=True)
class TXRouteWiringInventory:
    generated_at: str
    status: str
    routes: list[RouteFunctionWiring]
    remaining_boundaries: list[str]


def _decorator_text(lines: list[str], node: ast.AST) -> str:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return ""
    chunks: list[str] = []
    for decorator in node.decorator_list:
        start = decorator.lineno - 1
        end = decorator.end_lineno or decorator.lineno
        chunks.append("\n".join(lines[start:end]))
    return "\n".join(chunks)


def _source_segment(lines: list[str], node: ast.AST) -> str:
    start = getattr(node, "lineno", 1) - 1
    end = getattr(node, "end_lineno", getattr(node, "lineno", 1))
    return "\n".join(lines[start:end])


def _is_route(lines: list[str], node: ast.AST) -> bool:
    return "router." in _decorator_text(lines, node)


def _mutation_candidate(domain: str, name: str, source: str) -> bool:
    text = f"{name}\n{source}".lower()
    return any(hint in text for hint in MUTATION_HINTS.get(domain, []))


def _transactional_marker_present(domain: str, whole_source: str, function_source: str) -> bool:
    markers = TRANSACTIONAL_SERVICE_MARKERS.get(domain, [])
    return any(marker in function_source or marker in whole_source for marker in markers)


def scan_route_file(domain: str, path: Path) -> list[RouteFunctionWiring]:
    if not path.exists():
        return []
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    lines = source.splitlines()
    rows: list[RouteFunctionWiring] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not _is_route(lines, node):
            continue
        fn_source = _source_segment(lines, node)
        candidate = _mutation_candidate(domain, node.name, fn_source)
        marker = _transactional_marker_present(domain, source, fn_source)
        if candidate and marker:
            status = "route-transaction-marker-present"
        elif candidate:
            status = "route-transaction-wiring-not-proven"
        else:
            status = "read-or-nonmutation-route"
        rows.append(
            RouteFunctionWiring(
                domain=domain,
                path=path.relative_to(ROOT).as_posix(),
                function_name=node.name,
                line=node.lineno,
                is_route=True,
                mutation_candidate=candidate,
                transactional_marker_present=marker,
                status=status,
            )
        )

    return sorted(rows, key=lambda row: (row.domain, row.path, row.line))


def build_inventory() -> TXRouteWiringInventory:
    routes: list[RouteFunctionWiring] = []
    for domain, path in ROUTE_FILES.items():
        routes.extend(scan_route_file(domain, path))

    not_proven = [row for row in routes if row.status == "route-transaction-wiring-not-proven"]

    return TXRouteWiringInventory(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        status="production-route-transaction-wiring-not-proven" if not_proven else "production-route-transaction-markers-present",
        routes=routes,
        remaining_boundaries=[
            "route handlers must be wired through transactional application services",
            "live database transaction rollback behavior must be proven",
            "staging route smoke must be attached",
            "isolated rollback proof services do not prove production route wiring",
        ],
    )


def write_inventory() -> TXRouteWiringInventory:
    inventory = build_inventory()
    OUT_JSON.write_text(json.dumps(asdict(inventory), indent=2), encoding="utf-8")

    lines = [
        "# Transaction Route Wiring Inventory",
        "",
        f"Generated at: `{inventory.generated_at}`",
        "",
        f"**Status:** `{inventory.status}`",
        "",
        "| Domain | Route function | File | Line | Mutation candidate | Transaction marker | Status |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for row in inventory.routes:
        lines.append(
            f"| `{row.domain}` | `{row.function_name}` | `{row.path}` | {row.line} | "
            f"{row.mutation_candidate} | {row.transactional_marker_present} | `{row.status}` |"
        )

    lines.extend(["", "## Remaining boundaries", ""])
    lines.extend(f"- {item}" for item in inventory.remaining_boundaries)
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This inventory deliberately separates isolated rollback proof from production route wiring proof.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return inventory


__all__ = [
    "MUTATION_HINTS",
    "ROUTE_FILES",
    "TRANSACTIONAL_SERVICE_MARKERS",
    "TXRouteWiringInventory",
    "RouteFunctionWiring",
    "build_inventory",
    "write_inventory",
]
