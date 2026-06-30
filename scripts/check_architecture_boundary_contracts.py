#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STRICT_ROUTERS = {
    "app/api_v2_routers/popia.py": {
        "forbidden_import_prefixes": ("app.repositories",),
        "forbidden_imports": ("app.core.database", "sqlalchemy.ext.asyncio"),
        "required_imports": ("app.api_v2_deps.consent_lifecycle",),
    },
    "app/api_v2_routers/lessons.py": {
        "forbidden_import_prefixes": ("app.repositories",),
        "forbidden_imports": (),
        "required_imports": ("app.services.lesson_authorization",),
    },
}
AUTH_TRANSITION_ALLOWLIST = {"app/repositories/learner_repository.py", "app/repositories/repositories.py"}


def imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            modules.append(node.module or "")
        elif isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
    return sorted(set(modules))


def main() -> int:
    failures: list[str] = []
    print("Architecture boundary contract check")

    # Regenerate maps first.
    for command in [
        [sys.executable, "scripts/generate_service_family_map.py"],
        [sys.executable, "scripts/generate_router_service_dependency_map.py"],
        [sys.executable, "scripts/generate_legacy_learner_access_guard_report.py"],
    ]:
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        if result.returncode != 0:
            failures.append(f"{' '.join(command)} failed: {result.stdout}")

    for router, contract in STRICT_ROUTERS.items():
        path = ROOT / router
        if not path.exists():
            failures.append(f"{router} missing")
            print(f"- FAIL {router}: missing")
            continue

        modules = imports(path)
        for required in contract["required_imports"]:
            if required in modules:
                print(f"- PASS {router}: required import {required}")
            else:
                failures.append(f"{router}: missing required import {required}")
                print(f"- FAIL {router}: missing required import {required}")

        for forbidden in contract["forbidden_imports"]:
            if forbidden in modules:
                failures.append(f"{router}: forbidden import {forbidden}")
                print(f"- FAIL {router}: forbidden import {forbidden}")
            else:
                print(f"- PASS {router}: forbidden import absent {forbidden}")

        for prefix in contract["forbidden_import_prefixes"]:
            offenders = [m for m in modules if m.startswith(prefix)]
            if offenders:
                failures.append(f"{router}: forbidden {prefix} imports {offenders}")
                print(f"- FAIL {router}: forbidden imports {offenders}")
            else:
                print(f"- PASS {router}: no {prefix} imports")

    import_linter = ROOT / ".importlinter"
    if import_linter.exists():
        print("- PASS .importlinter exists")
    else:
        failures.append(".importlinter missing")
        print("- FAIL .importlinter missing")

    policy = ROOT / "docs/architecture/service_boundary_classification_policy.md"
    if policy.exists():
        print("- PASS service boundary classification policy exists")
    else:
        failures.append("service boundary classification policy missing")
        print("- FAIL service boundary classification policy missing")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS architecture boundary contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
