#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8") if p.exists() else ""


def main() -> int:
    failures: list[str] = []
    print("Runtime blocker repair check")
    adapter = read("app/services/popia_consent_lifecycle_adapter.py")
    for method in ("grant", "deny", "withdraw", "revoke", "renew"):
        if f"async def {method}" not in adapter:
            failures.append(f"POPIA adapter missing {method}")
    consent_dep = read("app/api_v2_deps/consent_lifecycle.py")
    if "POPIAConsentLifecycleAdapter" not in consent_dep:
        failures.append("consent dependency missing POPIA adapter")
    auth = read("app/api_v2_routers/auth.py")
    if "learners" in auth:
        failures.append("auth.py still contains `learners` token")
    for token in ("LearnerRepository(", "ConsentRepository(", "GuardianRepository("):
        if token in auth:
            failures.append(f"auth.py direct constructor remains: {token}")
    diagnostics = read("app/api_v2_routers/diagnostics.py")
    if "require_items=False" in diagnostics:
        failures.append("diagnostics still uses require_items=False")
    jobs = read("app/modules/jobs.py")
    for name in ("send_consent_reminders", "send_consent_renewal_reminders"):
        if f"async def {name}" not in jobs:
            failures.append(f"jobs missing {name}")
    for token in ("AsyncSessionLocal", "ConsentService("):
        if token in jobs:
            failures.append(f"jobs.py still directly references {token}")
    for path in [
        "app/services/popia_consent_lifecycle_adapter.py",
        "app/services/job_dependency_factory.py",
        "app/services/auth_runtime_boundary.py",
        "app/api_v2_routers/auth.py",
        "app/modules/jobs.py",
    ]:
        ast.parse(read(path))
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "app/api_v2_routers/auth.py", "app/modules/jobs.py", "app/api_v2_routers/popia.py", "app/api_v2_routers/diagnostics.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode != 0:
        print("- WARN focused ruff check reported issues:")
        print(ruff.stdout)
    else:
        print("- PASS focused ruff check")
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS runtime blocker repair check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
