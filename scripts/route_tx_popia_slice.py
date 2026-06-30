from __future__ import annotations

import ast
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POPIA_ROUTER = ROOT / "app/api_v2_routers/popia.py"
TX_ROUTE_INVENTORY_JSON = ROOT / "docs/architecture/tx_route_wiring_inventory.json"
OUT_JSON = ROOT / "docs/release/popia_route_transaction_slice_report.json"
OUT_MD = ROOT / "docs/release/popia_route_transaction_slice_report.md"
LIVE_DB_EVIDENCE = ROOT / "docs/release/popia_route_transaction_live_db_evidence.md"

DIRECT_DB_MUTATION_METHODS = {
    "add",
    "add_all",
    "commit",
    "delete",
    "execute",
    "flush",
    "merge",
    "refresh",
    "rollback",
}

SERVICE_NAME_HINTS = {
    "consent",
    "consent_svc",
    "consent_service",
    "dsr_svc",
    "popia_service",
    "lifecycle_service",
    "transactional_service",
    "deletion_service",
    "data_rights_service",
    "audit_service",
    "export_service",
    "correction_service",
    "restriction_service",
}

TRANSACTION_MARKERS = {
    "TransactionalPOPIAConsentLifecycleService",
    "TransactionalPOPIA",
    "async with self.session.begin",
    "async with session.begin",
    "async with db.begin",
    ".begin()",
}

PENDING_VALUES = {"", "pending", "todo", "tbd", "null", "none", "n/a", "unknown", "not set"}


@dataclass(frozen=True)
class POPIARouteSliceFinding:
    route_function: str
    line: int
    selected_from_inventory: bool
    service_delegate_calls: list[str]
    direct_db_mutations: list[str]
    route_source_status: str
    reason: str


@dataclass(frozen=True)
class POPIARouteTransactionSliceReport:
    generated_at: str
    current_commit: str
    route_file: str
    local_status: str
    live_db_status: str
    selected_route_count: int
    transaction_service_markers_found: list[str]
    findings: list[POPIARouteSliceFinding]
    blockers: list[str]
    no_false_closure_rules: list[str]


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _load_inventory() -> dict[str, Any]:
    if TX_ROUTE_INVENTORY_JSON.exists():
        return json.loads(TX_ROUTE_INVENTORY_JSON.read_text(encoding="utf-8"))
    try:
        from scripts.tx_route_wiring_inventory import write_inventory

        write_inventory()
    except Exception:
        return {"routes": [], "status": "missing-inventory"}
    if TX_ROUTE_INVENTORY_JSON.exists():
        return json.loads(TX_ROUTE_INVENTORY_JSON.read_text(encoding="utf-8"))
    return {"routes": [], "status": "missing-inventory"}


def _selected_popia_route_names() -> set[str]:
    inventory = _load_inventory()
    names: set[str] = set()
    for row in inventory.get("routes") or []:
        if row.get("domain") != "popia":
            continue
        if row.get("mutation_candidate") is True and row.get("status") == "route-transaction-wiring-not-proven":
            name = str(row.get("function_name") or "").strip()
            if name:
                names.add(name)
    return names


def _decorator_text(lines: list[str], node: ast.AST) -> str:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return ""
    chunks: list[str] = []
    for decorator in node.decorator_list:
        start = decorator.lineno - 1
        end = decorator.end_lineno or decorator.lineno
        chunks.append("\n".join(lines[start:end]))
    return "\n".join(chunks)


def _is_route(lines: list[str], node: ast.AST) -> bool:
    return "router." in _decorator_text(lines, node)


def _call_name(call: ast.Call) -> str:
    func = call.func
    if isinstance(func, ast.Attribute):
        parts = [func.attr]
        value = func.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        return ".".join(reversed(parts))
    if isinstance(func, ast.Name):
        return func.id
    return ""


def _direct_db_mutations(node: ast.AsyncFunctionDef | ast.FunctionDef) -> list[str]:
    mutations: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = _call_name(child)
            if name.startswith("db.") and name.split(".", 1)[1] in DIRECT_DB_MUTATION_METHODS:
                mutations.append(name)
    return sorted(set(mutations))


def _service_delegate_calls(node: ast.AsyncFunctionDef | ast.FunctionDef) -> list[str]:
    calls: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = _call_name(child)
            first = name.split(".", 1)[0]
            if first in SERVICE_NAME_HINTS and "." in name:
                calls.append(name)
    return sorted(set(calls))


def _service_marker_source() -> str:
    chunks: list[str] = []
    for root in [ROOT / "app/services", ROOT / "app/modules"]:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            lower = path.as_posix().lower()
            if "popia" not in lower and "consent" not in lower and "privacy" not in lower:
                continue
            try:
                chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
    return "\n".join(chunks)


def _transaction_service_markers_found() -> list[str]:
    source = _service_marker_source()
    return sorted(marker for marker in TRANSACTION_MARKERS if marker in source)


def _is_pending(value: str) -> bool:
    normalized = value.strip().strip("`").lower()
    return normalized in PENDING_VALUES or normalized.startswith("pending")


def _field(text: str, name: str) -> str:
    pattern = rf"\*\*{re.escape(name)}:\*\*\s*(.+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip().strip("`").strip() if match else ""


def live_db_template() -> str:
    return "\n".join(
        [
            "# POPIA Route Transaction Live DB Evidence",
            "",
            "**Item:** ROUTE-TX-POPIA-001",
            "",
            "**Route slice:** selected POPIA mutation routes",
            "",
            "**Live DB evidence URL:** pending",
            "",
            "**Test result:** pending",
            "",
            "**Database:** pending",
            "",
            "**Commit SHA:** pending",
            "",
            "**Verified by:** pending",
            "",
            "**Date verified:** pending",
            "",
            "## Required proof",
            "",
            "- Route-level negative tests execute the production POPIA route path.",
            "- Injected failures roll back all partial POPIA/data-rights/audit writes.",
            "- Evidence is produced against a real database transaction boundary.",
            "",
            "## No false-closure rule",
            "",
            "This file is not live DB proof while any field remains pending or while test result is not `passed`.",
            "",
        ]
    )


def write_live_db_template() -> None:
    if LIVE_DB_EVIDENCE.exists() and "**Item:** ROUTE-TX-POPIA-001" in LIVE_DB_EVIDENCE.read_text(encoding="utf-8"):
        return
    LIVE_DB_EVIDENCE.write_text(live_db_template(), encoding="utf-8")


def live_db_status() -> tuple[str, list[str]]:
    write_live_db_template()
    text = LIVE_DB_EVIDENCE.read_text(encoding="utf-8")
    fields = {
        "Live DB evidence URL": _field(text, "Live DB evidence URL"),
        "Test result": _field(text, "Test result"),
        "Database": _field(text, "Database"),
        "Commit SHA": _field(text, "Commit SHA"),
        "Verified by": _field(text, "Verified by"),
        "Date verified": _field(text, "Date verified"),
    }
    blockers: list[str] = []
    for name, value in fields.items():
        if _is_pending(value):
            blockers.append(f"{name} is pending")
    if fields["Live DB evidence URL"] and not fields["Live DB evidence URL"].startswith(("https://", "http://")):
        blockers.append("Live DB evidence URL must be a URL")
    if fields["Test result"].strip().lower() not in {"passed", "pass", "green", "ok"}:
        blockers.append("Test result must be passed/pass/green/ok")
    if fields["Commit SHA"] and not re.fullmatch(r"[0-9a-fA-F]{7,40}", fields["Commit SHA"]):
        blockers.append("Commit SHA must look like a git SHA")
    return ("live-db-proof-accepted" if not blockers else "external-blocked", blockers)


def _route_functions(tree: ast.AST, lines: list[str]) -> list[ast.AsyncFunctionDef | ast.FunctionDef]:
    funcs: list[ast.AsyncFunctionDef | ast.FunctionDef] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and _is_route(lines, node):
            funcs.append(node)
    return sorted(funcs, key=lambda node: node.lineno)


def build_report() -> POPIARouteTransactionSliceReport:
    blockers: list[str] = []
    findings: list[POPIARouteSliceFinding] = []
    selected = _selected_popia_route_names()

    if not POPIA_ROUTER.exists():
        blockers.append("POPIA router file missing")
        tree: ast.AST = ast.Module(body=[], type_ignores=[])
        lines: list[str] = []
    else:
        source = POPIA_ROUTER.read_text(encoding="utf-8")
        tree = ast.parse(source)
        lines = source.splitlines()

    route_nodes = _route_functions(tree, lines)
    if not selected:
        selected = {
            node.name
            for node in route_nodes
            if any(hint in node.name.lower() for hint in ["consent", "export", "deletion", "correction", "restriction"])
        }

    for node in route_nodes:
        if node.name not in selected:
            continue
        delegates = _service_delegate_calls(node)
        mutations = _direct_db_mutations(node)

        if delegates and not mutations:
            status = "route-delegates-to-service-boundary"
            reason = "route delegates to service boundary and has no direct db mutation calls"
        else:
            status = "not-proven"
            reasons: list[str] = []
            if not delegates:
                reasons.append("no POPIA service delegate call found")
            if mutations:
                reasons.append("direct db mutations present: " + ", ".join(mutations))
            reason = "; ".join(reasons)
            blockers.append(f"{node.name}: {reason}")

        findings.append(
            POPIARouteSliceFinding(
                route_function=node.name,
                line=node.lineno,
                selected_from_inventory=node.name in selected,
                service_delegate_calls=delegates,
                direct_db_mutations=mutations,
                route_source_status=status,
                reason=reason,
            )
        )

    if selected and not findings:
        blockers.append("selected POPIA routes were not found in router source")

    markers = _transaction_service_markers_found()
    if not markers:
        blockers.append("no POPIA transactional service markers found")

    live_status, live_blockers = live_db_status()
    local_blockers = [blocker for blocker in blockers if not blocker.startswith("live-db:")]
    local_status = "route-popia-delegation-passing" if not local_blockers else "route-popia-delegation-not-proven"

    return POPIARouteTransactionSliceReport(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        route_file="app/api_v2_routers/popia.py",
        local_status=local_status,
        live_db_status=live_status,
        selected_route_count=len(findings),
        transaction_service_markers_found=markers,
        findings=findings,
        blockers=blockers + [f"live-db: {blocker}" for blocker in live_blockers],
        no_false_closure_rules=[
            "POPIA route delegation does not prove live database rollback.",
            "Service markers do not prove the production route path by themselves.",
            "ROUTE-TX-POPIA-001 release mode requires live DB evidence.",
            "TX-ROUTE-001 remains open until all mutation route slices are wired and proven.",
        ],
    )


def write_report() -> POPIARouteTransactionSliceReport:
    report = build_report()
    OUT_JSON.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    lines = [
        "# POPIA Route Transaction Slice Report",
        "",
        f"Generated at: `{report.generated_at}`",
        f"Commit: `{report.current_commit}`",
        "",
        f"- Route file: `{report.route_file}`",
        f"- Local status: `{report.local_status}`",
        f"- Live DB status: `{report.live_db_status}`",
        f"- Selected route count: `{report.selected_route_count}`",
        "",
        "## Route findings",
        "",
        "| Route function | Line | Delegate calls | Direct DB mutations | Status |",
        "|---|---:|---|---|---|",
    ]
    for finding in report.findings:
        lines.append(
            f"| `{finding.route_function}` | {finding.line} | "
            f"`{', '.join(finding.service_delegate_calls) or '-'}` | "
            f"`{', '.join(finding.direct_db_mutations) or '-'}` | `{finding.route_source_status}` |"
        )

    lines.extend(["", "## Transaction service markers found", ""])
    if report.transaction_service_markers_found:
        lines.extend(f"- `{marker}`" for marker in report.transaction_service_markers_found)
    else:
        lines.append("- None")

    lines.extend(["", "## Blockers", ""])
    if report.blockers:
        lines.extend(f"- {blocker}" for blocker in report.blockers)
    else:
        lines.append("- None")

    lines.extend(["", "## No false-closure rules", ""])
    lines.extend(f"- {rule}" for rule in report.no_false_closure_rules)

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This report proves only the local POPIA route delegation slice. It does not prove live database rollback.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return report


__all__ = [
    "POPIARouteSliceFinding",
    "POPIARouteTransactionSliceReport",
    "build_report",
    "live_db_status",
    "write_report",
]
