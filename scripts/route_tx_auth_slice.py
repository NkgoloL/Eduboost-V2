from __future__ import annotations

import ast
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH_ROUTER = ROOT / "app/api_v2_routers/auth.py"
SERVICES_DIR = ROOT / "app/services"
OUT_JSON = ROOT / "docs/release/auth_route_transaction_slice_report.json"
OUT_MD = ROOT / "docs/release/auth_route_transaction_slice_report.md"
LIVE_DB_EVIDENCE = ROOT / "docs/release/auth_route_transaction_live_db_evidence.md"

TARGET_ROUTES = {
    "register": "auth_service.register",
    "create_dev_session": "auth_service.create_dev_session",
}

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

TRANSACTION_MARKERS = {
    "TransactionalAuthRegistrationService",
    "async with self.session.begin",
    "async with session.begin",
    "async with db.begin",
    ".begin()",
}

PENDING_VALUES = {"", "pending", "todo", "tbd", "null", "none", "n/a", "unknown", "not set"}


@dataclass(frozen=True)
class AuthRouteSliceFinding:
    route_function: str
    line: int
    expected_delegate: str
    delegate_found: bool
    auth_service_dependency_found: bool
    direct_db_mutations: list[str]
    status: str
    reason: str


@dataclass(frozen=True)
class AuthRouteTransactionSliceReport:
    generated_at: str
    current_commit: str
    route_file: str
    local_status: str
    live_db_status: str
    transaction_service_markers_found: list[str]
    findings: list[AuthRouteSliceFinding]
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


def _source_segment(lines: list[str], node: ast.AST) -> str:
    start = getattr(node, "lineno", 1) - 1
    end = getattr(node, "end_lineno", getattr(node, "lineno", 1))
    return "\n".join(lines[start:end])


def _find_function(tree: ast.AST, name: str) -> ast.AsyncFunctionDef | ast.FunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and node.name == name:
            return node
    return None


def _has_arg(node: ast.AsyncFunctionDef | ast.FunctionDef, arg_name: str) -> bool:
    return any(arg.arg == arg_name for arg in node.args.args + node.args.kwonlyargs)


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


def _delegate_found(node: ast.AsyncFunctionDef | ast.FunctionDef, expected: str) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and _call_name(child) == expected:
            return True
    return False


def _direct_db_mutations(node: ast.AsyncFunctionDef | ast.FunctionDef) -> list[str]:
    mutations: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = _call_name(child)
            if name.startswith("db.") and name.split(".", 1)[1] in DIRECT_DB_MUTATION_METHODS:
                mutations.append(name)
    return sorted(set(mutations))


def _service_marker_source() -> str:
    if not SERVICES_DIR.exists():
        return ""
    chunks: list[str] = []
    for path in SERVICES_DIR.rglob("*.py"):
        if "auth" not in path.name.lower() and "registration" not in path.name.lower():
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
            "# Auth Route Transaction Live DB Evidence",
            "",
            "**Item:** ROUTE-TX-AUTH-001",
            "",
            "**Route slice:** auth/register and auth/dev-session",
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
            "- Route-level negative tests execute the production route path.",
            "- Injected failures roll back all partial auth writes.",
            "- Evidence is produced against a real database transaction boundary.",
            "",
            "## No false-closure rule",
            "",
            "This file is not live DB proof while any field remains pending or while test result is not `passed`.",
            "",
        ]
    )


def write_live_db_template() -> None:
    if LIVE_DB_EVIDENCE.exists() and "**Item:** ROUTE-TX-AUTH-001" in LIVE_DB_EVIDENCE.read_text(encoding="utf-8"):
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


def build_report() -> AuthRouteTransactionSliceReport:
    blockers: list[str] = []
    findings: list[AuthRouteSliceFinding] = []

    if not AUTH_ROUTER.exists():
        blockers.append("auth router file missing")
        source = ""
        tree: ast.AST = ast.Module(body=[], type_ignores=[])
    else:
        source = AUTH_ROUTER.read_text(encoding="utf-8")
        tree = ast.parse(source)

    for route_name, expected_delegate in TARGET_ROUTES.items():
        node = _find_function(tree, route_name)
        if node is None:
            finding = AuthRouteSliceFinding(
                route_function=route_name,
                line=0,
                expected_delegate=expected_delegate,
                delegate_found=False,
                auth_service_dependency_found=False,
                direct_db_mutations=[],
                status="not-proven",
                reason="route function missing",
            )
            findings.append(finding)
            blockers.append(f"{route_name}: route function missing")
            continue

        delegate = _delegate_found(node, expected_delegate)
        dependency = _has_arg(node, "auth_service")
        mutations = _direct_db_mutations(node)
        if delegate and dependency and not mutations:
            status = "route-delegates-to-auth-service"
            reason = "route delegates mutation to auth service boundary and has no direct db mutation calls"
        else:
            status = "not-proven"
            missing: list[str] = []
            if not delegate:
                missing.append(f"expected delegate {expected_delegate} missing")
            if not dependency:
                missing.append("auth_service dependency missing")
            if mutations:
                missing.append("direct db mutations present: " + ", ".join(mutations))
            reason = "; ".join(missing)
            blockers.append(f"{route_name}: {reason}")

        findings.append(
            AuthRouteSliceFinding(
                route_function=route_name,
                line=node.lineno,
                expected_delegate=expected_delegate,
                delegate_found=delegate,
                auth_service_dependency_found=dependency,
                direct_db_mutations=mutations,
                status=status,
                reason=reason,
            )
        )

    markers = _transaction_service_markers_found()
    if not markers:
        blockers.append("no auth transactional service markers found in app/services")

    live_status, live_blockers = live_db_status()
    local_status = "route-auth-delegation-passing" if not blockers else "route-auth-delegation-not-proven"

    return AuthRouteTransactionSliceReport(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        route_file="app/api_v2_routers/auth.py",
        local_status=local_status,
        live_db_status=live_status,
        transaction_service_markers_found=markers,
        findings=findings,
        blockers=blockers + [f"live-db: {blocker}" for blocker in live_blockers],
        no_false_closure_rules=[
            "Route delegation does not prove live database rollback.",
            "Auth service markers do not prove the production route path by themselves.",
            "ROUTE-TX-AUTH-001 release mode requires live DB evidence.",
            "TX-ROUTE-001 remains open until all mutation route slices are wired and proven.",
        ],
    )


def write_report() -> AuthRouteTransactionSliceReport:
    report = build_report()
    OUT_JSON.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    lines = [
        "# Auth Route Transaction Slice Report",
        "",
        f"Generated at: `{report.generated_at}`",
        f"Commit: `{report.current_commit}`",
        "",
        f"- Route file: `{report.route_file}`",
        f"- Local status: `{report.local_status}`",
        f"- Live DB status: `{report.live_db_status}`",
        "",
        "## Route findings",
        "",
        "| Route function | Line | Delegate | Delegate found | Auth service dependency | Direct DB mutations | Status |",
        "|---|---:|---|---:|---:|---|---|",
    ]
    for finding in report.findings:
        lines.append(
            f"| `{finding.route_function}` | {finding.line} | `{finding.expected_delegate}` | "
            f"{finding.delegate_found} | {finding.auth_service_dependency_found} | "
            f"`{', '.join(finding.direct_db_mutations) or '-'}` | `{finding.status}` |"
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
            "This report proves only the local auth route delegation slice. It does not prove live database rollback.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return report


__all__ = [
    "TARGET_ROUTES",
    "AuthRouteSliceFinding",
    "AuthRouteTransactionSliceReport",
    "build_report",
    "live_db_status",
    "write_report",
]
