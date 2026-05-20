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
OUT_JSON = ROOT / "docs/release/auth_route_logout_delegate_status.json"
OUT_MD = ROOT / "docs/release/auth_route_logout_delegate_status.md"
TARGETS = ("logout", "revoke_all_tokens")


@dataclass(frozen=True)
class TargetStatus:
    route: str
    exists: bool
    has_auth_service_param: bool
    delegates_to_service: bool
    direct_cookie_or_token_logic: list[str]
    passed: bool


@dataclass(frozen=True)
class Status:
    generated_at: str
    current_commit: str
    status: str
    targets: list[TargetStatus]
    blockers: list[str]


def current_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def parse_auth() -> ast.AST:
    return ast.parse(read(AUTH_ROUTER) or "\n")


def find_func(tree: ast.AST, name: str) -> ast.AsyncFunctionDef | ast.FunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and node.name == name:
            return node
    return None


def call_name(call: ast.Call) -> str:
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


def route_has_auth_service_param(node: ast.AsyncFunctionDef | ast.FunctionDef | None) -> bool:
    if node is None:
        return False
    return any(arg.arg == "auth_service" for arg in list(node.args.args) + list(node.args.kwonlyargs))


def route_delegates(node: ast.AsyncFunctionDef | ast.FunctionDef | None, route: str) -> bool:
    if node is None:
        return False
    return any(isinstance(child, ast.Call) and call_name(child) == f"auth_service.{route}" for child in ast.walk(node))


def direct_logic(node: ast.AsyncFunctionDef | ast.FunctionDef | None) -> list[str]:
    if node is None:
        return []
    found: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = call_name(child)
            if name.endswith("delete_cookie") or name.endswith("set_cookie"):
                found.add(name)
            if name in {"consume_refresh_token", "revoke_all_refresh_tokens", "create_access_token"}:
                found.add(name)
    return sorted(found)


def _find_provider_import() -> str:
    for path in (ROOT / "app/api_v2_deps").rglob("*.py"):
        if "get_auth_application_service" in read(path):
            module = path.relative_to(ROOT).with_suffix("").as_posix().replace("/", ".")
            return f"from {module} import get_auth_application_service"
    return "from app.api_v2_deps.auth_service import get_auth_application_service"


def _ensure_imports(source: str) -> str:
    changed = source
    if "AuthApplicationService" not in changed:
        changed = "from app.services.auth_application_service import AuthApplicationService\n" + changed
    if "get_auth_application_service" not in changed:
        changed = _find_provider_import() + "\n" + changed
    if re.search(r"(?m)^from fastapi import .*$", changed):
        def repl(match: re.Match[str]) -> str:
            line = match.group(0)
            names = line.split("import", 1)[1]
            needed = []
            if "Depends" not in names:
                needed.append("Depends")
            if "Response" not in names:
                needed.append("Response")
            return line + (", " + ", ".join(needed) if needed else "")
        changed = re.sub(r"(?m)^from fastapi import .*$", repl, changed, count=1)
    else:
        changed = "from fastapi import Depends, Response\n" + changed
    return changed


def _signature_end(lines: list[str], start: int) -> int:
    depth = 0
    for index in range(start, len(lines)):
        line = lines[index]
        depth += line.count("(") - line.count(")")
        if depth <= 0 and line.rstrip().endswith(":"):
            return index
    return start


def _ensure_auth_service_param(lines: list[str], node: ast.AsyncFunctionDef | ast.FunctionDef) -> list[str]:
    if route_has_auth_service_param(node):
        return lines
    start = node.lineno - 1
    end = _signature_end(lines, start)
    signature = "\n".join(lines[start:end + 1])
    param = "auth_service: AuthApplicationService = Depends(get_auth_application_service)"
    close = signature.rfind(")")
    if close < 0:
        return lines
    signature = signature[:close] + ", " + param + signature[close:]
    return lines[:start] + signature.splitlines() + lines[end + 1:]


def _body_kwargs(node: ast.AsyncFunctionDef | ast.FunctionDef) -> str:
    args = {arg.arg for arg in list(node.args.args) + list(node.args.kwonlyargs)}
    names = [name for name in ["response", "request", "current_user", "db", "refresh_token"] if name in args]
    return ", ".join(f"{name}={name}" for name in names)


def _replace_body(lines: list[str], node: ast.AsyncFunctionDef | ast.FunctionDef, route: str) -> list[str]:
    body_start = node.body[0].lineno - 1 if node.body else node.lineno
    end = node.end_lineno or body_start + 1
    indent = re.match(r"^(\s*)", lines[body_start]).group(1) if body_start < len(lines) else "    "
    kwargs = _body_kwargs(node)
    call = f"return await auth_service.{route}({kwargs})" if kwargs else f"return await auth_service.{route}()"
    return lines[:body_start] + [indent + call] + lines[end:]


def repair() -> Status:
    if not AUTH_ROUTER.exists():
        return write_status()
    source = _ensure_imports(read(AUTH_ROUTER))
    for route in TARGETS:
        tree = ast.parse(source)
        node = find_func(tree, route)
        if node is None:
            continue
        lines = source.splitlines()
        lines = _ensure_auth_service_param(lines, node)
        source = "\n".join(lines) + "\n"
        tree = ast.parse(source)
        node = find_func(tree, route)
        if node is not None and (not route_delegates(node, route) or direct_logic(node)):
            lines = source.splitlines()
            lines = _replace_body(lines, node, route)
            source = "\n".join(lines) + "\n"
    AUTH_ROUTER.write_text(source, encoding="utf-8")
    return write_status()


def build_status() -> Status:
    tree = parse_auth()
    targets: list[TargetStatus] = []
    blockers: list[str] = []
    for route in TARGETS:
        node = find_func(tree, route)
        exists = node is not None
        has_param = route_has_auth_service_param(node)
        delegates = route_delegates(node, route)
        direct = direct_logic(node)
        passed = exists and has_param and delegates and not direct
        if not passed:
            blockers.append(f"{route} route is not fully delegated to auth service")
        targets.append(TargetStatus(route, exists, has_param, delegates, direct, passed))
    return Status(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status="auth-route-logout-delegation-passing" if not blockers else "auth-route-logout-delegation-not-proven",
        targets=targets,
        blockers=blockers,
    )


def write_status() -> Status:
    status = build_status()
    OUT_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    lines = [
        "# Auth Route Logout/Revoke Delegation Status", "", f"Generated at: `{status.generated_at}`", f"Commit: `{status.current_commit}`", "",
        f"**Status:** `{status.status}`", "",
        "| Route | Exists | Auth service param | Delegates | Direct route logic | Passed |",
        "|---|---:|---:|---:|---|---:|",
    ]
    for target in status.targets:
        lines.append(f"| `{target.route}` | {target.exists} | {target.has_auth_service_param} | {target.delegates_to_service} | `{', '.join(target.direct_cookie_or_token_logic) or '-'}` | {target.passed} |")
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {blocker}" for blocker in status.blockers)
    if not status.blockers:
        lines.append("- None")
    lines.extend(["", "## No false-closure rules", "", "- Route body delegation does not prove HTTP behavior.", "- Logout/revoke HTTP proof remains a separate batch.", "- This cleanup does not approve beta release.", ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return status
