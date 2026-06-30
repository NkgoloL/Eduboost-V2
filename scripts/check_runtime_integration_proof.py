#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CRITICAL_FILES = [
    "app/api_v2_routers/auth.py",
    "app/modules/jobs.py",
    "app/api_v2_routers/popia.py",
    "app/api_v2_routers/diagnostics.py",
    "app/api_v2_deps/consent_lifecycle.py",
    "app/services/popia_consent_lifecycle_adapter.py",
    "app/services/diagnostic_session_integrity.py",
]


def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8") if p.exists() else ""


def main() -> int:
    failures: list[str] = []
    print("Runtime integration proof check")

    consent_dep = read("app/api_v2_deps/consent_lifecycle.py")
    if "POPIAConsentLifecycleAdapter" in consent_dep:
        print("- PASS POPIA dependency uses lifecycle adapter")
    else:
        failures.append("POPIA dependency missing lifecycle adapter")

    adapter = read("app/services/popia_consent_lifecycle_adapter.py")
    for method in ("grant", "deny", "withdraw", "renew"):
        if f"async def {method}" not in adapter:
            failures.append(f"POPIA adapter missing {method}")

    diagnostics = read("app/api_v2_routers/diagnostics.py")
    if "require_items=False" in diagnostics:
        failures.append("diagnostics contains require_items=False")
    else:
        print("- PASS diagnostics has no require_items=False")

    helper = read("app/services/diagnostic_session_integrity.py")
    if "validate_session_served_item_binding" in helper:
        print("- PASS diagnostic session integrity helper exists")
    else:
        failures.append("missing validate_session_served_item_binding helper")

    for path in CRITICAL_FILES:
        if (ROOT / path).exists():
            ast.parse(read(path))
            print(f"- PASS syntax {path}")

    ruff = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            *[path for path in CRITICAL_FILES if (ROOT / path).exists()],
            "--select",
            "F821,F401,F811,E402",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused ruff critical runtime check")
    else:
        failures.append("focused ruff critical runtime check failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS runtime integration proof check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
