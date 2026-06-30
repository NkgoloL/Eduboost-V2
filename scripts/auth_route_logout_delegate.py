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
PARAM_NAME = "auth_service"
PARAM_TEXT = "auth_service: AuthApplicationService = Depends(get_auth_application_service)"
DIRECT_LOGIC_NAMES = {"consume_refresh_token", "revoke_all_refresh_tokens", "create_access_token"}


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
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def read_auth() -> str:
    return AUTH_ROUTER.read_text(encoding="utf-8", errors="ignore") if AUTH_ROUTER.exists() else ""


def write_auth(source: str) -> None:
    AUTH_ROUTER.write_text(source, encoding="utf-8")


def strip_malformed_auth_service_param_lines(source: str) -> str:
    """Remove standalone parameter lines left by previous broken scripts."""
    bad = re.compile(
        r"^\s*,?\s*auth_service\s*:\s*AuthApplicationService\s*=\s*Depends\(get_auth_application_service\)\s*,?\s*$"
    )
    lines = [line for line in source.splitlines() if not bad.match(line)]
    return "\n".join(lines) + "\n"


def parse_source(source: str | None = None) -> ast.Module:
    return ast.parse(source if source is not None else read_auth() or "\n")


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


def has_auth_service_param(node: ast.AsyncFunctionDef | ast.FunctionDef | None) -> bool:
    if node is None:
        return False
    args = list(node.args.args) + list(node.args.kwonlyargs)
    return any(arg.arg == PARAM_NAME for arg in args)


def delegates_to_service(node: ast.AsyncFunctionDef | ast.FunctionDef | None, route: str) -> bool:
    if node is None:
        return False
    expected = f"auth_service.{route}"
    return any(isinstance(child, ast.Call) and call_name(child) == expected for child in ast.walk(node))


def direct_route_logic(node: ast.AsyncFunctionDef | ast.FunctionDef | None) -> list[str]:
    if node is None:
        return []
    found: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = call_name(child)
            if name.endswith("delete_cookie") or name.endswith("set_cookie"):
                found.add(name)
            if name in DIRECT_LOGIC_NAMES:
                found.add(name)
    return sorted(found)


def _insertion_index_after_header(lines: list[str]) -> int:
    index = 0
    if lines and (lines[0].startswith('"""') or lines[0].startswith("'''")):
        quote = lines[0][:3]
        index = 1
        while index < len(lines) and not lines[index].endswith(quote):
            index += 1
        index = min(index + 1, len(lines))
    while index < len(lines) and (lines[index].strip() == "" or lines[index].startswith("from __future__")):
        index += 1
    return index


def _insert_import(source: str, import_line: str) -> str:
    if import_line in source:
        return source
    lines = source.splitlines()
    index = _insertion_index_after_header(lines)
    lines.insert(index, import_line)
    return "\n".join(lines) + "\n"


def _fastapi_imports(source: str) -> set[str]:
    names: set[str] = set()
    for match in re.finditer(r"(?m)^from fastapi import (?P<names>.+)$", source):
        for name in match.group("names").split(","):
            names.add(name.strip().split(" as ", 1)[0])
    return names


def ensure_imports(source: str) -> str:
    if "AuthApplicationService" not in source:
        source = _insert_import(source, "from app.services.auth_application_service import AuthApplicationService")
    if "get_auth_application_service" not in source:
        source = _insert_import(source, "from app.api_v2_deps.auth_service import get_auth_application_service")
    if "Depends" not in _fastapi_imports(source):
        source = _insert_import(source, "from fastapi import Depends")
    return source


def _signature_end(lines: list[str], start: int) -> int:
    depth = 0
    started = False
    for index in range(start, len(lines)):
        line = lines[index]
        if "def " in line:
            started = True
        depth += line.count("(") - line.count(")")
        if started and depth <= 0 and line.rstrip().endswith(":"):
            return index
    return start


def _previous_param_line_index(lines: list[str], start: int, end: int) -> int | None:
    for index in range(end - 1, start, -1):
        stripped = lines[index].strip()
        if stripped and not stripped.startswith("#"):
            return index
    return None


def ensure_auth_service_param(source: str, route: str) -> str:
    tree = parse_source(source)
    node = find_func(tree, route)
    if node is None or has_auth_service_param(node):
        return source

    lines = source.splitlines()
    start = node.lineno - 1
    end = _signature_end(lines, start)

    if start == end:
        close = lines[start].rfind(")")
        if close < 0:
            return source
        lines[start] = lines[start][:close] + f", {PARAM_TEXT}" + lines[start][close:]
        return "\n".join(lines) + "\n"

    previous = _previous_param_line_index(lines, start, end)
    if previous is not None and not lines[previous].rstrip().endswith((",", "(")):
        lines[previous] = lines[previous].rstrip() + ","

    def_indent = re.match(r"^(\s*)", lines[start]).group(1)
    param_indent = def_indent + "    "
    lines.insert(end, f"{param_indent}{PARAM_TEXT},")
    return "\n".join(lines) + "\n"


def _function_arg_names(node: ast.AsyncFunctionDef | ast.FunctionDef) -> list[str]:
    args = list(node.args.args) + list(node.args.kwonlyargs)
    return [arg.arg for arg in args if arg.arg != PARAM_NAME]


def replace_body_with_delegation(source: str, route: str) -> str:
    tree = parse_source(source)
    node = find_func(tree, route)
    if node is None:
        return source

    lines = source.splitlines()
    body_start = node.body[0].lineno - 1 if node.body else node.lineno
    body_end = node.end_lineno or body_start + 1
    indent = re.match(r"^(\s*)", lines[body_start]).group(1) if body_start < len(lines) else "    "
    kwargs = ", ".join(f"{name}={name}" for name in _function_arg_names(node))
    call = f"return await auth_service.{route}({kwargs})" if kwargs else f"return await auth_service.{route}()"
    return "\n".join(lines[:body_start] + [indent + call] + lines[body_end:]) + "\n"


def repair() -> Status:
    if not AUTH_ROUTER.exists():
        return write_status()

    source = strip_malformed_auth_service_param_lines(read_auth())
    source = ensure_imports(source)
    parse_source(source)

    for route in TARGETS:
        source = ensure_auth_service_param(source, route)
        parse_source(source)
        source = replace_body_with_delegation(source, route)
        parse_source(source)

    write_auth(source)
    return write_status()


def build_status() -> Status:
    source = read_auth()
    tree = parse_source(source)
    targets: list[TargetStatus] = []
    blockers: list[str] = []

    for route in TARGETS:
        node = find_func(tree, route)
        exists = node is not None
        has_param = has_auth_service_param(node)
        delegates = delegates_to_service(node, route)
        direct = direct_route_logic(node)
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
        "# Auth Route Logout/Revoke Delegation Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "| Route | Exists | Auth service param | Delegates | Direct route logic | Passed |",
        "|---|---:|---:|---:|---|---:|",
    ]
    for target in status.targets:
        lines.append(
            f"| `{target.route}` | {target.exists} | {target.has_auth_service_param} | "
            f"{target.delegates_to_service} | `{', '.join(target.direct_cookie_or_token_logic) or '-'}` | {target.passed} |"
        )
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {blocker}" for blocker in status.blockers)
    if not status.blockers:
        lines.append("- None")
    lines.extend([
        "",
        "## No false-closure rules",
        "",
        "- Route body delegation does not prove HTTP behavior.",
        "- Logout/revoke HTTP proof remains a separate batch.",
        "- This cleanup does not approve beta release.",
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return status
