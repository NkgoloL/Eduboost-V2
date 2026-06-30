#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
AUTH_ROUTER = ROOT / "app/api_v2_routers/auth.py"


def main() -> int:
    failures: list[str] = []
    print("Auth router boundary check")

    subprocess.run([sys.executable, "scripts/inspect_auth_router_boundary.py"], cwd=ROOT, check=True)

    source = AUTH_ROUTER.read_text(encoding="utf-8")

    if "app.api_v2_deps.auth_runtime" in source:
        print("- PASS auth router imports runtime dependency module")
    else:
        failures.append("missing auth runtime dependency import")
        print("- FAIL auth router missing runtime dependency module import")

    if "LearnerRepository(" not in source and "LearnerRepository" not in source:
        print("- PASS auth router has no direct LearnerRepository symbol")
    else:
        failures.append("LearnerRepository remains in auth router")
        print("- FAIL LearnerRepository remains in auth router")

    if ".get_by_guardian(" not in source:
        print("- PASS auth router has no direct get_by_guardian call")
    else:
        failures.append("direct get_by_guardian remains")
        print("- FAIL direct get_by_guardian remains in auth router")

    service_impl = (ROOT / "app/services/auth_lifecycle_impl.py").read_text(encoding="utf-8")
    if "auth_runtime.guardian_learner_ids" in service_impl or "guardian_learner_ids" in service_impl:
        print("- PASS guardian learner scope still referenced for refresh claims in service impl")
    else:
        failures.append("guardian learner ids not referenced in service impl")
        print("- FAIL guardian learner ids not referenced in service impl")

    report = ROOT / "docs/release/auth_router_boundary_repair_report.md"
    if report.exists():
        print("- PASS repair report exists")
    else:
        failures.append("missing repair report")
        print("- FAIL repair report missing")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS auth router boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
