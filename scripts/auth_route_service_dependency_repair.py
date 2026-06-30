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
OUT_JSON = ROOT / "docs/release/auth_route_service_dependency_repair_status.json"
OUT_MD = ROOT / "docs/release/auth_route_service_dependency_repair_status.md"
PARAM = "auth_service: AuthApplicationService = Depends(get_auth_application_service)"


@dataclass(frozen=True)
class FunctionStatus:
    function: str
    line: int
    references_auth_service: bool
    has_auth_service_param: bool
    passed: bool


@dataclass(frozen=True)
class Status:
    generated_at: str
    current_commit: str
    status: str
    functions: list[FunctionStatus]
    blockers: list[str]


def current_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def read_auth() -> str:
    return AUTH_ROUTER.read_text(encoding="utf-8", errors="ignore") if AUTH_ROUTER.exists() else ""


def parse(source: str | None = None) -> ast.AST:
    return ast.parse(read_auth() if source is None else source)


def _is_route(node: ast.AST) -> bool:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    return any("router." in ast.unparse(dec) for dec in node.decorator_list)


def _references_auth_service(node: ast.AST) -> bool:
    return any(isinstance(child, ast.Name) and child.id == "auth_service" for child in ast.walk(node))


def _has_param(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(arg.arg == "auth_service" for arg in [*node.args.args, *node.args.kwonlyargs])


def _insert_after_header(source: str, line: str) -> str:
    if line in source:
        return source
    lines = source.splitlines()
    idx = 0
    if lines and lines[0].startswith(chr(34) * 3):
        quote = chr(34) * 3
        idx = 1
        while idx < len(lines) and not lines[idx].endswith(quote):
            idx += 1
        idx = min(idx + 1, len(lines))
    while idx < len(lines) and (not lines[idx].strip() or lines[idx].startswith("from __future__")):
        idx += 1
    lines.insert(idx, line)
    return "\n".join(lines) + "\n"


def _provider_import() -> str:
    deps = ROOT / "app/api_v2_deps"
    if deps.exists():
        for path in deps.rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "get_auth_application_service" in text:
                module = path.relative_to(ROOT).with_suffix("").as_posix().replace("/", ".")
                return f"from {module} import get_auth_application_service"
    return "from app.api_v2_deps.auth_service import get_auth_application_service"


def ensure_imports(source: str) -> str:
    source = _insert_after_header(source, "from app.services.auth_application_service import AuthApplicationService")
    if not re.search(r"(?m)^from .* import .*get_auth_application_service", source):
        source = _insert_after_header(source, _provider_import())
    match = re.search(r"(?m)^from fastapi import (?P<names>.+)$", source)
    if match:
        if "Depends" not in match.group("names"):
            source = source.replace(match.group(0), match.group(0) + ", Depends", 1)
    else:
        source = _insert_after_header(source, "from fastapi import Depends")
    return source


def _sig_end(lines: list[str], start: int) -> int:
    depth = 0
    for i in range(start, len(lines)):
        depth += lines[i].count("(") - lines[i].count(")")
        if depth <= 0 and lines[i].rstrip().endswith(":"):
            return i
    return start


def _find_func(source: str, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in ast.walk(parse(source)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def add_param(source: str, name: str) -> str:
    node = _find_func(source, name)
    if node is None or _has_param(node):
        return source

    lines = source.splitlines()
    start = node.lineno - 1
    end = _sig_end(lines, start)

    if start == end:
        idx = lines[start].rfind(")")
        if idx < 0:
            return source
        prefix = "" if lines[start][idx - 1] == "(" else ", "
        lines[start] = lines[start][:idx] + prefix + PARAM + lines[start][idx:]
        return "\n".join(lines) + "\n"

    close_indent = re.match(r"^(\s*)", lines[end]).group(1)
    insert_at = end
    prev = insert_at - 1
    while prev > start and not lines[prev].strip():
        prev -= 1
    stripped = lines[prev].rstrip()
    if stripped and not stripped.endswith(",") and not stripped.endswith("("):
        lines[prev] = stripped + ","
    lines.insert(insert_at, close_indent + "    " + PARAM + ",")
    return "\n".join(lines) + "\n"


def missing_auth_service_params(source: str) -> list[str]:
    missing: list[str] = []
    for node in ast.walk(parse(source)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_route(node):
            if _references_auth_service(node) and not _has_param(node):
                missing.append(node.name)
    return sorted(set(missing))


def repair() -> Status:
    source = ensure_imports(read_auth())
    parse(source)
    for _ in range(10):
        missing = missing_auth_service_params(source)
        if not missing:
            break
        for name in missing:
            source = add_param(source, name)
            parse(source)
    AUTH_ROUTER.write_text(source, encoding="utf-8")
    return write_status()


def build_status() -> Status:
    functions: list[FunctionStatus] = []
    blockers: list[str] = []
    for node in sorted([n for n in ast.walk(parse()) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))], key=lambda n: n.lineno):
        if not _is_route(node):
            continue
        refs = _references_auth_service(node)
        has = _has_param(node)
        passed = (not refs) or has
        if not passed:
            blockers.append(f"{node.name} references auth_service without dependency parameter")
        functions.append(FunctionStatus(node.name, node.lineno, refs, has, passed))
    return Status(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status="auth-route-service-dependencies-passing" if not blockers else "auth-route-service-dependencies-not-proven",
        functions=functions,
        blockers=blockers,
    )


def write_status() -> Status:
    status = build_status()
    OUT_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    lines = [
        "# Auth Route Service Dependency Repair Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "| Function | Line | References auth_service | Has dependency param | Passed |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in status.functions:
        lines.append(f"| `{item.function}` | {item.line} | {item.references_auth_service} | {item.has_auth_service_param} | {item.passed} |")
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {b}" for b in status.blockers)
    if not status.blockers:
        lines.append("- None")
    lines.extend(["", "## No false-closure rules", "", "- F821-free route source does not prove HTTP auth behavior.", "- Auth lifecycle HTTP proof remains separate.", "- This repair does not approve beta release.", ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return status
