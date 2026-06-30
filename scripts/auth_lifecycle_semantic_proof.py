from __future__ import annotations

import ast
import asyncio
import importlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
AUTH_ROUTER = ROOT / "app/api_v2_routers/auth.py"
AUTH_SERVICE = ROOT / "app/services/auth_application_service.py"
OUT_JSON = ROOT / "docs/release/auth_lifecycle_semantic_proof_status.json"
OUT_MD = ROOT / "docs/release/auth_lifecycle_semantic_proof_status.md"

TARGETS = ("register", "login", "refresh", "logout", "revoke_all_tokens")
COOKIE_TARGETS = ("logout", "revoke_all_tokens")
PROHIBITED_ROUTE_CALLS = {
    "response.delete_cookie",
    "response.set_cookie",
    "consume_refresh_token",
    "revoke_all_refresh_tokens",
    "create_access_token",
    "create_refresh_token",
}


@dataclass(frozen=True)
class RouteSemanticProof:
    function: str
    delegates_to_service: bool
    has_auth_service_param: bool
    passes_context_keywords: list[str]
    prohibited_route_calls: list[str]
    passed: bool


@dataclass(frozen=True)
class ServiceCookieProof:
    method: str
    callable_ok: bool
    deleted_cookies: list[str]
    returned_mapping: bool
    passed: bool
    detail: str


@dataclass(frozen=True)
class Status:
    generated_at: str
    current_commit: str
    status: str
    route_proofs: list[RouteSemanticProof]
    cookie_proofs: list[ServiceCookieProof]
    blockers: list[str]


class FakeResponse:
    def __init__(self) -> None:
        self.deleted_cookies: list[str] = []

    def delete_cookie(self, key: str, *args, **kwargs) -> None:
        self.deleted_cookies.append(key)


def current_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def parse(path: Path = AUTH_ROUTER) -> ast.AST:
    return ast.parse(read(path) or "\n")


def route_functions() -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    tree = parse(AUTH_ROUTER)
    funcs: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any("router." in ast.unparse(dec) for dec in node.decorator_list):
                funcs[node.name] = node
    return funcs


def class_methods(path: Path, class_name: str = "AuthApplicationService") -> set[str]:
    tree = parse(path)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
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


def has_auth_service_param(node: ast.FunctionDef | ast.AsyncFunctionDef | None) -> bool:
    if node is None:
        return False
    return any(arg.arg == "auth_service" for arg in [*node.args.args, *node.args.kwonlyargs])


def delegates_to_service(node: ast.FunctionDef | ast.AsyncFunctionDef | None, method: str) -> bool:
    if node is None:
        return False
    expected = f"auth_service.{method}"
    return any(isinstance(child, ast.Call) and call_name(child) == expected for child in ast.walk(node))


def service_call_keywords(node: ast.FunctionDef | ast.AsyncFunctionDef | None, method: str) -> list[str]:
    if node is None:
        return []
    expected = f"auth_service.{method}"
    names: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and call_name(child) == expected:
            for keyword in child.keywords:
                if keyword.arg:
                    names.add(keyword.arg)
    return sorted(names)


def prohibited_calls(node: ast.FunctionDef | ast.AsyncFunctionDef | None) -> list[str]:
    if node is None:
        return []
    found: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = call_name(child)
            if name in PROHIBITED_ROUTE_CALLS or name.endswith(".delete_cookie") or name.endswith(".set_cookie"):
                found.add(name)
    return sorted(found)


async def _call_cookie_method(method: str) -> ServiceCookieProof:
    try:
        service_module = importlib.import_module("app.services.auth_application_service")
        service_cls = getattr(service_module, "AuthApplicationService")
        service = object.__new__(service_cls)

        services_pkg = importlib.import_module("app.services")
        old_impl = getattr(services_pkg, "auth_lifecycle_impl", None)
        setattr(services_pkg, "auth_lifecycle_impl", SimpleNamespace())
        try:
            response = FakeResponse()
            result = getattr(service, method)(response=response)
            if asyncio.iscoroutine(result):
                result = await result
            returned_mapping = isinstance(result, dict)
            deleted = list(response.deleted_cookies)
            return ServiceCookieProof(
                method=method,
                callable_ok=True,
                deleted_cookies=deleted,
                returned_mapping=returned_mapping,
                passed="refresh_token" in deleted and returned_mapping,
                detail="controlled fallback invocation completed",
            )
        finally:
            if old_impl is not None:
                setattr(services_pkg, "auth_lifecycle_impl", old_impl)
    except Exception as exc:
        return ServiceCookieProof(method, False, [], False, False, f"{exc.__class__.__name__}: {exc}")


def route_semantic_proofs() -> list[RouteSemanticProof]:
    functions = route_functions()
    proofs: list[RouteSemanticProof] = []
    for method in TARGETS:
        node = functions.get(method)
        delegated = delegates_to_service(node, method)
        has_param = has_auth_service_param(node)
        keywords = service_call_keywords(node, method)
        prohibited = prohibited_calls(node)
        proofs.append(RouteSemanticProof(method, delegated, has_param, keywords, prohibited, delegated and has_param and not prohibited))
    return proofs


async def _cookie_semantic_proofs() -> list[ServiceCookieProof]:
    return [await _call_cookie_method(method) for method in COOKIE_TARGETS]


def cookie_semantic_proofs() -> list[ServiceCookieProof]:
    return asyncio.run(_cookie_semantic_proofs())


def build_status() -> Status:
    routes = route_semantic_proofs()
    cookies = cookie_semantic_proofs()
    service_methods = class_methods(AUTH_SERVICE)

    blockers: list[str] = []
    for method in TARGETS:
        if method not in service_methods:
            blockers.append(f"AuthApplicationService missing {method}")
    for proof in routes:
        if not proof.passed:
            blockers.append(f"{proof.function} route semantic delegation incomplete")
    for proof in cookies:
        if not proof.passed:
            blockers.append(f"{proof.method} controlled cookie clearing proof failed: {proof.detail}")

    return Status(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status="auth-lifecycle-controlled-semantic-proof-passing" if not blockers else "auth-lifecycle-controlled-semantic-proof-not-proven",
        route_proofs=routes,
        cookie_proofs=cookies,
        blockers=blockers,
    )


def write_status() -> Status:
    status = build_status()
    OUT_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    lines = [
        "# Auth Lifecycle Controlled Semantic Proof Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "## Route semantic proof",
        "",
        "| Function | Delegates | Has auth_service dependency | Passed context keywords | Prohibited route calls | Passed |",
        "|---|---:|---:|---|---|---:|",
    ]
    for proof in status.route_proofs:
        lines.append(
            f"| `{proof.function}` | {proof.delegates_to_service} | {proof.has_auth_service_param} | "
            f"`{', '.join(proof.passes_context_keywords) or '-'}` | `{', '.join(proof.prohibited_route_calls) or '-'}` | {proof.passed} |"
        )
    lines.extend(["", "## Controlled cookie proof", "", "| Method | Callable | Deleted cookies | Returned mapping | Detail | Passed |", "|---|---:|---|---:|---|---:|"])
    for proof in status.cookie_proofs:
        lines.append(
            f"| `{proof.method}` | {proof.callable_ok} | `{', '.join(proof.deleted_cookies) or '-'}` | "
            f"{proof.returned_mapping} | {proof.detail} | {proof.passed} |"
        )
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {blocker}" for blocker in status.blockers)
    if not status.blockers:
        lines.append("- None")
    lines.extend([
        "",
        "## No false-closure rules",
        "",
        "- Controlled fallback invocation does not prove production repository revocation.",
        "- This does not prove refresh-token reuse detection against Redis/Postgres.",
        "- This does not prove cookie behavior in a real browser/client.",
        "- This proof does not approve beta release.",
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return status
