from __future__ import annotations

import ast
import importlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTH_ROUTER = ROOT / "app/api_v2_routers/auth.py"
AUTH_SERVICE = ROOT / "app/services/auth_application_service.py"
OUT_JSON = ROOT / "docs/release/auth_lifecycle_http_proof_status.json"
OUT_MD = ROOT / "docs/release/auth_lifecycle_http_proof_status.md"

TARGETS = {
    "register": "register",
    "login": "login",
    "refresh": "refresh",
    "logout": "logout",
    "revoke_all_tokens": "revoke_all_tokens",
}


@dataclass(frozen=True)
class LifecycleRouteProof:
    function: str
    service_method: str
    source_route_exists: bool
    registered_route_exists: bool
    service_method_exists: bool
    has_auth_service_dependency: bool
    delegates_to_service: bool
    methods: list[str]
    paths: list[str]
    passed: bool


@dataclass(frozen=True)
class Status:
    generated_at: str
    current_commit: str
    status: str
    router_import_ok: bool
    synthetic_app_registration_ok: bool
    proofs: list[LifecycleRouteProof]
    blockers: list[str]


def current_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def parse(path: Path) -> ast.AST:
    return ast.parse(read(path) or "\n")


def class_methods(path: Path, class_name: str) -> set[str]:
    tree = parse(path)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}
    return set()


def route_functions() -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    tree = parse(AUTH_ROUTER)
    found: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any("router." in ast.unparse(dec) for dec in node.decorator_list):
                found[node.name] = node
    return found


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


def has_auth_service_dependency(node: ast.FunctionDef | ast.AsyncFunctionDef | None) -> bool:
    if node is None:
        return False
    args = [*node.args.args, *node.args.kwonlyargs]
    return any(arg.arg == "auth_service" for arg in args)


def delegates_to_service(node: ast.FunctionDef | ast.AsyncFunctionDef | None, method: str) -> bool:
    if node is None:
        return False
    expected = f"auth_service.{method}"
    return any(isinstance(child, ast.Call) and call_name(child) == expected for child in ast.walk(node))


def registered_routes() -> tuple[bool, bool, dict[str, dict[str, list[str]]]]:
    try:
        auth_module = importlib.import_module("app.api_v2_routers.auth")
        router = getattr(auth_module, "router")
    except Exception:
        return False, False, {}

    try:
        from fastapi import FastAPI
        from fastapi.routing import APIRoute

        app = FastAPI()
        app.include_router(router)
        routes: dict[str, dict[str, list[str]]] = {}
        for route in app.routes:
            if not isinstance(route, APIRoute):
                continue
            endpoint_name = getattr(route.endpoint, "__name__", "")
            routes.setdefault(endpoint_name, {"paths": [], "methods": []})
            routes[endpoint_name]["paths"].append(route.path)
            routes[endpoint_name]["methods"].extend(sorted(route.methods or []))
        return True, True, routes
    except Exception:
        return True, False, {}


def build_status() -> Status:
    source_routes = route_functions()
    service_methods = class_methods(AUTH_SERVICE, "AuthApplicationService")
    router_import_ok, registration_ok, registered = registered_routes()

    proofs: list[LifecycleRouteProof] = []
    blockers: list[str] = []

    if not router_import_ok:
        blockers.append("auth router import failed")
    if not registration_ok:
        blockers.append("auth router synthetic FastAPI registration failed")

    for function, method in TARGETS.items():
        node = source_routes.get(function)
        registered_info = registered.get(function, {"paths": [], "methods": []})
        proof = LifecycleRouteProof(
            function=function,
            service_method=method,
            source_route_exists=node is not None,
            registered_route_exists=bool(registered_info["paths"]),
            service_method_exists=method in service_methods,
            has_auth_service_dependency=has_auth_service_dependency(node),
            delegates_to_service=delegates_to_service(node, method),
            methods=sorted(set(registered_info["methods"])),
            paths=sorted(set(registered_info["paths"])),
            passed=(
                node is not None
                and bool(registered_info["paths"])
                and method in service_methods
                and has_auth_service_dependency(node)
                and delegates_to_service(node, method)
            ),
        )
        if not proof.passed:
            blockers.append(f"{function} HTTP route/service proof incomplete")
        proofs.append(proof)

    return Status(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status="auth-lifecycle-http-route-proof-passing" if not blockers else "auth-lifecycle-http-route-proof-not-proven",
        router_import_ok=router_import_ok,
        synthetic_app_registration_ok=registration_ok,
        proofs=proofs,
        blockers=blockers,
    )


def write_status() -> Status:
    status = build_status()
    OUT_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# Auth Lifecycle HTTP Route Proof Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        f"**Router import OK:** `{status.router_import_ok}`",
        f"**Synthetic app registration OK:** `{status.synthetic_app_registration_ok}`",
        "",
        "| Function | Service method | Source route | Registered | Service method | Dependency | Delegates | Methods | Paths | Passed |",
        "|---|---|---:|---:|---:|---:|---:|---|---|---:|",
    ]
    for proof in status.proofs:
        lines.append(
            f"| `{proof.function}` | `{proof.service_method}` | {proof.source_route_exists} | "
            f"{proof.registered_route_exists} | {proof.service_method_exists} | "
            f"{proof.has_auth_service_dependency} | {proof.delegates_to_service} | "
            f"`{', '.join(proof.methods) or '-'}` | `{', '.join(proof.paths) or '-'}` | {proof.passed} |"
        )

    lines.extend(["", "## Blockers", ""])
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend([
        "",
        "## No false-closure rules",
        "",
        "- Route registration/source proof does not prove database-backed auth semantics.",
        "- Cookie persistence and refresh-token revocation semantics remain separate runtime concerns.",
        "- This proof does not approve beta release.",
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return status


__all__ = [
    "LifecycleRouteProof",
    "Status",
    "build_status",
    "class_methods",
    "delegates_to_service",
    "has_auth_service_dependency",
    "registered_routes",
    "route_functions",
    "write_status",
]
