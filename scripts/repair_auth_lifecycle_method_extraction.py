#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "app/api_v2_routers/auth.py"
SERVICE = ROOT / "app/services/auth_application_service.py"
REPORT = ROOT / "docs/release/auth_lifecycle_method_extraction_repair_report.md"
BLOCKER = ROOT / "docs/release/auth_lifecycle_method_extraction_blockers.md"

TARGET_METHODS = {
    "register": ("register",),
    "login": ("login",),
    "refresh": ("refresh", "refresh_token"),
    "create_dev_session": ("dev_session", "create_dev_session", "dev"),
}

MARKER = "# code_911_950_auth_lifecycle_delegate"
SERVICE_MARKER = "# code_911_950_auth_lifecycle_methods"


def _write_blocker(lines: list[str]) -> None:
    BLOCKER.write_text(
        "\n".join(
            [
                "# Auth Lifecycle Method Extraction Blocker",
                "",
                f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
                "",
                *lines,
                "",
            ]
        ),
        encoding="utf-8",
    )


def _ensure_import(text: str, import_line: str) -> str:
    module_part = import_line.split(" import ", 1)[0].replace("from ", "")
    if import_line.strip() in text or module_part in text:
        return text

    lines = text.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].startswith('"""'):
        insert_at = 1
        while insert_at < len(lines) and '"""' not in lines[insert_at]:
            insert_at += 1
        insert_at = min(insert_at + 1, len(lines))
    if insert_at < len(lines) and lines[insert_at].startswith("from __future__"):
        insert_at += 1
    while insert_at < len(lines) and (lines[insert_at].startswith("import ") or lines[insert_at].startswith("from ")):
        insert_at += 1
    lines.insert(insert_at, import_line if import_line.endswith("\n") else import_line + "\n")
    return "".join(lines)


def _remove_future_annotations(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines() if line.strip() != "from __future__ import annotations"
    ) + ("\n" if text.endswith("\n") else "")


def _decorator_text(source_lines: list[str], node: ast.AST) -> str:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return ""
    chunks: list[str] = []
    for decorator in node.decorator_list:
        start = decorator.lineno - 1
        end = decorator.end_lineno or decorator.lineno
        chunks.append("\n".join(source_lines[start:end]))
    return "\n".join(chunks)


def _target_for_name(name: str) -> str | None:
    lowered = name.lower()
    if lowered.startswith("_auth_lifecycle_legacy_"):
        return None
    for method, tokens in TARGET_METHODS.items():
        if any(token in lowered for token in tokens):
            if method == "create_dev_session":
                if "dev" in lowered and "session" in lowered:
                    return method
                if lowered in {"create_dev_session", "dev_session"}:
                    return method
                continue
            return method
    return None


def _route_nodes(source: str) -> list[tuple[ast.AsyncFunctionDef | ast.FunctionDef, str]]:
    tree = ast.parse(source)
    lines = source.splitlines()
    found: list[tuple[ast.AsyncFunctionDef | ast.FunctionDef, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            continue
        decorators = _decorator_text(lines, node)
        if "router." not in decorators and "@router" not in decorators:
            continue
        method = _target_for_name(node.name)
        if method is None:
            continue
        found.append((node, method))
    return sorted(found, key=lambda item: item[0].lineno)


def _header_and_body_lines(source_lines: list[str], node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[list[str], list[str]]:
    header_start = node.lineno - 1
    body_start = node.body[0].lineno - 1 if node.body else node.lineno
    end = node.end_lineno or node.lineno
    return source_lines[header_start:body_start], source_lines[body_start:end]


def _ensure_auth_service_param(header_lines: list[str]) -> list[str]:
    header_text = "\n".join(header_lines)
    if "auth_service" in header_text:
        return header_lines

    param = "auth_service: AuthApplicationService = Depends(get_auth_application_service)"

    if len(header_lines) == 1:
        line = header_lines[0]
        return [re.sub(r"\)\s*(->[^:]+)?:", rf", {param})\1:", line, count=1)]

    updated = list(header_lines)
    for idx in range(len(updated) - 1, -1, -1):
        if updated[idx].strip().endswith(":"):
            indent = re.match(r"^(\s*)", updated[idx]).group(1)
            updated.insert(idx, f"{indent}    {param},")
            return updated
    raise RuntimeError("Could not locate function signature closing line")


def _arg_names(node: ast.FunctionDef | ast.AsyncFunctionDef, include_auth_service: bool) -> list[str]:
    names = [arg.arg for arg in [*node.args.args, *node.args.kwonlyargs]]
    if include_auth_service and "auth_service" not in names:
        names.append("auth_service")
    return names


def _route_replacement(source_lines: list[str], node: ast.FunctionDef | ast.AsyncFunctionDef, method: str) -> str:
    deco_start = min((decorator.lineno for decorator in node.decorator_list), default=node.lineno) - 1
    decorators = source_lines[deco_start:node.lineno - 1]
    header_lines, body_lines = _header_and_body_lines(source_lines, node)
    route_header = _ensure_auth_service_param(header_lines)

    helper_name = f"_auth_lifecycle_legacy_{method}_impl"
    helper_header: list[str] = []
    first_replaced = False
    for line in route_header:
        if not first_replaced and re.search(r"\bdef\s+" + re.escape(node.name) + r"\b", line):
            helper_header.append(re.sub(r"\bdef\s+" + re.escape(node.name) + r"\b", f"def {helper_name}", line, count=1))
            first_replaced = True
        else:
            helper_header.append(line)

    arg_names = _arg_names(node, include_auth_service=True)
    call_lines = [f"        {name}={name}," for name in arg_names]

    body_indent = "    "
    if body_lines:
        body_indent = re.match(r"^(\s*)", body_lines[0]).group(1) or "    "

    wrapper_body = [
        f"{body_indent}{MARKER}",
        f"{body_indent}return await auth_service.{method}(",
        f"{body_indent}    legacy_impl={helper_name},",
        *[f"{body_indent}{line}" for line in call_lines],
        f"{body_indent})",
    ]

    replacement = decorators + route_header + wrapper_body + ["", *helper_header, *body_lines]
    return "\n".join(replacement)


def patch_auth_router() -> list[str]:
    if not AUTH.exists():
        _write_blocker(["Missing `app/api_v2_routers/auth.py`."])
        return []

    source = AUTH.read_text(encoding="utf-8")
    source = _remove_future_annotations(source)
    source = _ensure_import(source, "from app.api_v2_deps.auth_service import get_auth_application_service")
    source = _ensure_import(source, "from app.services.auth_application_service import AuthApplicationService")

    if MARKER in source:
        AUTH.write_text(source, encoding="utf-8")
        return []

    nodes = _route_nodes(source)
    if not nodes:
        _write_blocker(["No register/login/refresh/dev-session auth route functions were found."])
        return []

    lines = source.splitlines()
    replacements: list[tuple[int, int, str]] = []
    covered: set[str] = set()

    for node, method in nodes:
        if method in covered:
            continue
        covered.add(method)
        start = min((decorator.lineno for decorator in node.decorator_list), default=node.lineno) - 1
        end = node.end_lineno or node.lineno
        replacements.append((start, end, _route_replacement(lines, node, method)))

    for start, end, replacement in sorted(replacements, reverse=True):
        lines[start:end] = replacement.splitlines()

    updated = "\n".join(lines) + "\n"
    ast.parse(updated)
    AUTH.write_text(updated, encoding="utf-8")
    return sorted(covered)


def patch_service_methods() -> None:
    if not SERVICE.exists():
        _write_blocker(["Missing `app/services/auth_application_service.py`. Run code_871_910 first."])
        return

    text = SERVICE.read_text(encoding="utf-8")
    if SERVICE_MARKER in text:
        return

    addition = "\n".join(
        [
            "",
            "# code_911_950_auth_lifecycle_methods",
            "async def _auth_lifecycle_call_legacy(self, legacy_impl, **kwargs):",
            "    \"\"\"Execute a preserved auth lifecycle implementation through the service boundary.\"\"\"",
            "    if legacy_impl is None:",
            "        raise AuthApplicationServiceError(\"legacy_impl is required for transitional lifecycle extraction\")",
            "    result = legacy_impl(**kwargs)",
            "    if hasattr(result, \"__await__\"):",
            "        return await result",
            "    return result",
            "",
            "",
            "async def _auth_lifecycle_register(self, *, legacy_impl=None, **kwargs):",
            "    return await self._auth_lifecycle_call_legacy(legacy_impl, **kwargs)",
            "",
            "",
            "async def _auth_lifecycle_login(self, *, legacy_impl=None, **kwargs):",
            "    return await self._auth_lifecycle_call_legacy(legacy_impl, **kwargs)",
            "",
            "",
            "async def _auth_lifecycle_refresh(self, *, legacy_impl=None, **kwargs):",
            "    return await self._auth_lifecycle_call_legacy(legacy_impl, **kwargs)",
            "",
            "",
            "async def _auth_lifecycle_create_dev_session(self, *, legacy_impl=None, **kwargs):",
            "    return await self._auth_lifecycle_call_legacy(legacy_impl, **kwargs)",
            "",
            "",
            "AuthApplicationService._auth_lifecycle_call_legacy = _auth_lifecycle_call_legacy",
            "AuthApplicationService.register = _auth_lifecycle_register",
            "AuthApplicationService.login = _auth_lifecycle_login",
            "AuthApplicationService.refresh = _auth_lifecycle_refresh",
            "AuthApplicationService.create_dev_session = _auth_lifecycle_create_dev_session",
            "",
        ]
    )
    SERVICE.write_text(text.rstrip() + "\n" + addition, encoding="utf-8")


def main() -> int:
    patched = patch_auth_router()
    patch_service_methods()

    auth_text = AUTH.read_text(encoding="utf-8") if AUTH.exists() else ""
    service_text = SERVICE.read_text(encoding="utf-8") if SERVICE.exists() else ""

    failures: list[str] = []
    for method in ("register", "login", "refresh"):
        if f"auth_service.{method}(" not in auth_text:
            failures.append(f"auth.py does not delegate {method}")
        if f"AuthApplicationService.{method}" not in service_text:
            failures.append(f"AuthApplicationService missing assigned {method} method")

    if failures:
        _write_blocker(["Failures after lifecycle extraction:", "", *[f"- {item}" for item in failures]])
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    REPORT.write_text(
        "\n".join(
            [
                "# Auth Lifecycle Method Extraction Repair Report",
                "",
                f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
                "",
                "**Status:** implemented",
                "",
                "## Delegated lifecycle methods",
                "",
                *(f"- `{method}`" for method in patched),
                "",
                "## Boundary",
                "",
                "Routes now delegate through AuthApplicationService methods. Original route bodies are preserved as private `_auth_lifecycle_legacy_*_impl` helpers to avoid behavior changes while completing the service-boundary transition.",
                "",
                "## Remaining debt",
                "",
                "- Move private legacy helper bodies out of auth.py into AuthApplicationService proper.",
                "- Add full HTTP request/response integration tests for register/login/refresh/dev-session.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    if BLOCKER.exists():
        BLOCKER.unlink()

    print(f"Patched {AUTH.relative_to(ROOT)}")
    print(f"Patched {SERVICE.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
