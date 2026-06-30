#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
CRITICAL = [
    "app/services/arq_import_compat.py",
    "app/services/job_dependency_factory.py",
    "app/modules/jobs.py",
    "scripts/repair_arq_dependency_worker_import.py",
    "scripts/check_arq_worker_import.py",
    "tests/unit/test_arq_worker_import_contract.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _dependency_files_with_arq() -> list[str]:
    files = [
        "requirements/base.in",
        "requirements/base.txt",
        "requirements.txt",
        "requirements-dev.txt",
        "requirements/dev.in",
        "requirements/dev.txt",
    ]
    found = []
    for item in files:
        path = ROOT / item
        if path.exists() and any(line.strip().startswith("arq") for line in path.read_text(encoding="utf-8").splitlines()):
            found.append(item)
    return found


def _worker_function_names(jobs_module) -> set[str]:
    settings = getattr(jobs_module, "WorkerSettings", None)
    if settings is None:
        return set()
    functions = getattr(settings, "functions", [])
    return {getattr(fn, "__name__", str(fn)) for fn in functions}


def main() -> int:
    failures: list[str] = []
    print("ARQ dependency and worker import check")

    arq_files = _dependency_files_with_arq()
    if arq_files:
        print(f"- PASS arq pinned in: {', '.join(arq_files)}")
    else:
        failures.append("arq not pinned in dependency files")

    try:
        jobs = importlib.import_module("app.modules.jobs")
        print("- PASS imported app.modules.jobs")
    except Exception as exc:
        failures.append(f"app.modules.jobs import failed: {exc!r}")
        jobs = None

    try:
        compat = importlib.import_module("app.services.arq_import_compat")
        status = compat.arq_dependency_status()
        print(f"- PASS arq compat imports; available={status['available']}")
    except Exception as exc:
        failures.append(f"arq compat import failed: {exc!r}")

    if jobs is not None:
        names = _worker_function_names(jobs)
        for expected in (
            "send_consent_reminders",
            "send_consent_renewal_reminders",
            "generate_lesson_job",
            "generate_study_plan_job",
            "run_practice_session_cleanup",
        ):
            if expected in names or hasattr(jobs, expected):
                print(f"- PASS worker exposes {expected}")
            else:
                failures.append(f"WorkerSettings/functions missing {expected}")

    jobs_source = read("app/modules/jobs.py")
    if "run_consent_reminder_cycle" in jobs_source:
        print("- PASS jobs.py delegates consent reminder dependencies to job_dependency_factory")
    else:
        failures.append("jobs.py missing run_consent_reminder_cycle")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    pytest_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/unit/test_arq_worker_import_contract.py",
            "-q",
            "--no-cov",
            "--tb=short",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(pytest_result.stdout)
    if pytest_result.returncode == 0:
        print("- PASS ARQ worker import contract tests")
    else:
        failures.append("ARQ worker import contract tests failed")

    ruff = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            *CRITICAL,
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
        print("- PASS focused ruff ARQ worker check")
    else:
        failures.append("focused ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS ARQ dependency and worker import check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
