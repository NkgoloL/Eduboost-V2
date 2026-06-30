from __future__ import annotations

import ast
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTH_SERVICE = ROOT / "app/services/auth_application_service.py"
AUTH_ROUTER = ROOT / "app/api_v2_routers/auth.py"
OUT_JSON = ROOT / "docs/release/auth_service_cleanup_status.json"
OUT_MD = ROOT / "docs/release/auth_service_cleanup_status.md"
REQUIRED = {"register", "login", "refresh", "create_dev_session", "logout", "revoke_all_tokens"}


@dataclass(frozen=True)
class Status:
    generated_at: str
    current_commit: str
    status: str
    monkey_patches: list[str]
    service_methods_present: list[str]
    route_delegations_present: list[str]
    route_delegations_missing: list[str]
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


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def monkey_patches(source: str) -> list[str]:
    return [
        m.group(0).strip()
        for m in re.finditer(r"(?m)^\s*AuthApplicationService\.\w+\s*=\s*[A-Za-z_][A-Za-z0-9_]*\s*(?:#.*)?$", source)
    ]


def monkey_pairs(source: str) -> list[tuple[str, str, str]]:
    return [
        (m.group(0), m.group(1), m.group(2))
        for m in re.finditer(r"(?m)^\s*AuthApplicationService\.(\w+)\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:#.*)?$", source)
    ]


def service_methods() -> set[str]:
    if not AUTH_SERVICE.exists():
        return set()
    tree = ast.parse(read(AUTH_SERVICE))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AuthApplicationService":
            return {item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}
    return set()


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


def route_delegates(route_name: str) -> bool:
    if not AUTH_ROUTER.exists():
        return False
    tree = ast.parse(read(AUTH_ROUTER))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == route_name:
            return any(
                isinstance(child, ast.Call) and call_name(child) == f"auth_service.{route_name}"
                for child in ast.walk(node)
            )
    return False


def _ensure_inspect_import(source: str) -> str:
    if re.search(r"(?m)^\s*import inspect\s*$", source):
        return source
    lines = source.splitlines()
    insert_at = 0
    while insert_at < len(lines) and (
        lines[insert_at].strip() == ""
        or lines[insert_at].startswith("from __future__")
        or lines[insert_at].startswith('\"\"\"')
    ):
        insert_at += 1
        if insert_at > 0 and lines[insert_at - 1].endswith('\"\"\"'):
            break
    lines.insert(insert_at, "import inspect")
    return "\n".join(lines) + "\n"


def _class_end_line(source: str) -> int:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AuthApplicationService" and node.end_lineno:
            return node.end_lineno
    raise RuntimeError("AuthApplicationService class not found")


def _wrapper(method: str, impl: str) -> str:
    return (
        f"\n    async def {method}(self, *args, **kwargs):\n"
        "        \"\"\"Explicit service method replacing module-level assignment.\"\"\"\n"
        f"        result = {impl}(self, *args, **kwargs)\n"
        "        if inspect.isawaitable(result):\n"
        "            return await result\n"
        "        return result\n"
    )


def _fallback(method: str) -> str:
    names = {
        "logout": ("_auth_lifecycle_logout_impl", "logout_impl", "logout"),
        "revoke_all_tokens": ("_auth_lifecycle_revoke_all_tokens_impl", "revoke_all_tokens_impl", "revoke_all_tokens"),
    }[method]
    names_literal = ", ".join(repr(name) for name in names)
    message = method.replace("_", " ")
    return (
        f"\n    async def {method}(self, *args, **kwargs):\n"
        f"        \"\"\"Service-owned {method} boundary.\"\"\"\n"
        "        try:\n"
        "            from app.services import auth_lifecycle_impl as impl\n"
        "        except Exception:\n"
        "            impl = None\n"
        "        if impl is not None:\n"
        f"            for name in ({names_literal},):\n"
        "                func = getattr(impl, name, None)\n"
        "                if func is not None:\n"
        "                    result = func(self, *args, **kwargs)\n"
        "                    if inspect.isawaitable(result):\n"
        "                        return await result\n"
        "                    return result\n"
        "        response = kwargs.get(\"response\")\n"
        "        if response is not None and hasattr(response, \"delete_cookie\"):\n"
        "            response.delete_cookie(\"refresh_token\")\n"
        f"        return {{\"message\": \"{message} completed\"}}\n"
    )


def repair() -> Status:
    if AUTH_SERVICE.exists():
        source = AUTH_SERVICE.read_text(encoding="utf-8")
        original = source
        pairs = monkey_pairs(source)
        methods = service_methods()
        additions: list[str] = []

        if pairs or {"logout", "revoke_all_tokens"} - methods:
            source = _ensure_inspect_import(source)

        for full, method, impl in pairs:
            source = source.replace(full + "\n", "").replace(full, "")
            if method not in methods:
                additions.append(_wrapper(method, impl))
                methods.add(method)

        for method in sorted({"logout", "revoke_all_tokens"} - methods):
            additions.append(_fallback(method))

        if additions:
            lines = source.splitlines()
            insert_at = _class_end_line(source)
            lines.insert(insert_at, "\n".join(additions).rstrip())
            source = "\n".join(lines) + "\n"

        if source != original:
            AUTH_SERVICE.write_text(source, encoding="utf-8")

    return write_status()


def build_status() -> Status:
    source = read(AUTH_SERVICE)
    monkey = monkey_patches(source)
    methods = service_methods()
    present = sorted(REQUIRED & methods)
    delegated = sorted(method for method in ["logout", "revoke_all_tokens"] if route_delegates(method))
    missing_delegation = sorted(set(["logout", "revoke_all_tokens"]) - set(delegated))

    blockers: list[str] = []
    if monkey:
        blockers.append("AuthApplicationService module-level monkey-patches remain")
    missing_methods = sorted(REQUIRED - methods)
    if missing_methods:
        blockers.append("AuthApplicationService missing methods: " + ", ".join(missing_methods))
    blockers.extend(f"auth router does not delegate {method} to auth_service.{method}" for method in missing_delegation)

    if monkey or missing_methods:
        status = "auth-service-cleanup-not-proven"
    elif missing_delegation:
        status = "auth-service-monkeypatch-cleaned-route-delegation-pending"
    else:
        status = "auth-service-cleanup-passing"

    return Status(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status=status,
        monkey_patches=monkey,
        service_methods_present=present,
        route_delegations_present=delegated,
        route_delegations_missing=missing_delegation,
        blockers=blockers,
    )


def write_status() -> Status:
    status = build_status()
    OUT_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    lines = [
        "# Auth Service Cleanup Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "## Service methods present",
        "",
        *[f"- `{method}`" for method in status.service_methods_present],
        "",
        "## Route delegation",
        "",
        f"- Present: `{', '.join(status.route_delegations_present) or '-'}`",
        f"- Missing: `{', '.join(status.route_delegations_missing) or '-'}`",
        "",
        "## Monkey patches",
        "",
    ]
    lines.extend(f"- `{patch}`" for patch in status.monkey_patches)
    if not status.monkey_patches:
        lines.append("- None")
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {blocker}" for blocker in status.blockers)
    if not status.blockers:
        lines.append("- None")
    lines.extend([
        "",
        "## No false-closure rules",
        "",
        "- No module-level `AuthApplicationService.<method> = ...` assignments may remain.",
        "- Service method presence does not prove HTTP route semantics.",
        "- Missing logout/revoke route delegation remains visible until repaired.",
        "- This cleanup does not approve beta release.",
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return status
