#!/usr/bin/env python3
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def _import_optional(module_name: str) -> Any | None:
    try:
        module = __import__(module_name, fromlist=["*"])
        return module
    except Exception as exc:
        print(f"- WARN [import] {module_name}: {type(exc).__name__}: {exc}")
        return None


def _has_callable(obj: Any, name: str) -> bool:
    return hasattr(obj, name) and callable(getattr(obj, name))


def check_audit_runtime_surface() -> list[str]:
    failures: list[str] = []
    print("Audit runtime compatibility surface")

    compat = _import_optional("app.repositories.audit_compat")
    if compat is None:
        failures.append("missing app.repositories.audit_compat")
    else:
        for name in ["AuditRepositoryCompatAdapter", "AuditEventInput", "normalize_audit_kwargs"]:
            if hasattr(compat, name):
                print(f"- PASS [audit compat] {name}: present")
            else:
                print(f"- FAIL [audit compat] {name}: missing")
                failures.append(f"missing audit compat {name}")

    canonical = _import_optional("app.repositories.audit_repository")
    if canonical is not None:
        repo_cls = getattr(canonical, "AuditRepository", None)
        if repo_cls is None:
            print("- WARN [audit repository] AuditRepository class not found in canonical module")
        else:
            methods = [name for name, value in inspect.getmembers(repo_cls) if callable(value)]
            if any(name in methods for name in ["record", "append", "create"]):
                print("- PASS [audit repository] exposes record/append/create-compatible method")
            else:
                print("- FAIL [audit repository] lacks record/append/create-compatible method")
                failures.append("canonical AuditRepository lacks record/append/create")

    return failures


def check_consent_runtime_surface() -> list[str]:
    failures: list[str] = []
    print("Consent runtime compatibility surface")

    compat = _import_optional("app.services.consent_compat")
    if compat is None:
        failures.append("missing app.services.consent_compat")
    else:
        for name in ["ConsentAuditEvent", "normalize_consent_audit_event", "classify_consent_action"]:
            if hasattr(compat, name):
                print(f"- PASS [consent compat] {name}: present")
            else:
                print(f"- FAIL [consent compat] {name}: missing")
                failures.append(f"missing consent compat {name}")

    consent_modules = [
        "app.services.consent_service",
        "app.modules.consent.service",
        "app.services.popia_service",
    ]
    imported_any = False
    for module_name in consent_modules:
        module = _import_optional(module_name)
        if module is not None:
            imported_any = True
            print(f"- PASS [consent import] {module_name}: importable")

    if not imported_any:
        failures.append("no consent service module imported")

    return failures


def check_deep_health_surface() -> list[str]:
    failures: list[str] = []
    print("Deep-health compatibility surface")

    contract = REPO_ROOT / "docs/release/health_readiness_diagnostic_contract.md"
    if not contract.exists():
        print("- FAIL [health contract] missing")
        failures.append("missing health readiness contract")
    else:
        text = contract.read_text(encoding="utf-8")
        for needle in ["database connectivity", "Alembic current revision", "required core table presence"]:
            if needle in text:
                print(f"- PASS [health contract] contains {needle!r}")
            else:
                print(f"- FAIL [health contract] missing {needle!r}")
                failures.append(f"health contract missing {needle!r}")

    return failures


def main() -> int:
    failures: list[str] = []
    failures.extend(check_audit_runtime_surface())
    failures.extend(check_consent_runtime_surface())
    failures.extend(check_deep_health_surface())

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS backend runtime compatibility surface")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
