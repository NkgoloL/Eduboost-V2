#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTICS = ROOT / "app/api_v2_routers/diagnostics.py"
JOBS = ROOT / "app/modules/jobs.py"
CORE_JOBS = ROOT / "app/core/jobs.py"

MARKER_SUBMISSION = "# code_691_720_diagnostic_submission_integrity"
MARKER_MASTERY = "# code_691_720_mastery_theta_integrity"


def main() -> int:
    failures: list[str] = []
    print("Diagnostics and jobs integrity check")

    if (ROOT / "app/services/diagnostic_data_integrity.py").exists():
        print("- PASS diagnostic integrity helper exists")
    else:
        failures.append("missing diagnostic helper")
        print("- FAIL diagnostic integrity helper missing")

    if (ROOT / "app/services/job_runtime_integrity.py").exists():
        print("- PASS job runtime integrity helper exists")
    else:
        failures.append("missing job runtime helper")
        print("- FAIL job runtime helper missing")

    diagnostics_text = DIAGNOSTICS.read_text(encoding="utf-8") if DIAGNOSTICS.exists() else ""
    if "app.services.diagnostic_data_integrity" in diagnostics_text:
        print("- PASS diagnostics router imports integrity helper")
    else:
        failures.append("diagnostics helper import")
        print("- FAIL diagnostics router missing integrity helper import")

    if MARKER_SUBMISSION in diagnostics_text or MARKER_MASTERY in diagnostics_text:
        print("- PASS diagnostics router contains integrity markers")
    else:
        failures.append("diagnostics markers")
        print("- FAIL diagnostics router contains no integrity markers")

    jobs_text = JOBS.read_text(encoding="utf-8") if JOBS.exists() else ""
    if "ConsentService()" in jobs_text:
        failures.append("ConsentService empty constructor")
        print("- FAIL jobs module still contains ConsentService()")
    else:
        print("- PASS no ConsentService() empty constructor in jobs module")

    for token in ("AsyncSessionLocal", "ConsentRepository", "validate_arq_job_payload"):
        if token in jobs_text:
            print(f"- PASS jobs module contains {token}")
        else:
            failures.append(f"jobs missing {token}")
            print(f"- FAIL jobs module missing {token}")

    core_jobs_text = CORE_JOBS.read_text(encoding="utf-8") if CORE_JOBS.exists() else ""
    if "Durable workflows belong in" in core_jobs_text:
        print("- PASS FastAPI BackgroundTasks policy documented")
    else:
        failures.append("background task policy")
        print("- FAIL FastAPI BackgroundTasks policy missing")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS diagnostics and jobs integrity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
