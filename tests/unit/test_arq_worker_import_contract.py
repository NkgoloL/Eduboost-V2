from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_arq_dependency_is_declared_in_dependency_files():
    files = [
        ROOT / "requirements/base.in",
        ROOT / "requirements/base.txt",
        ROOT / "requirements.txt",
        ROOT / "requirements-dev.txt",
        ROOT / "requirements/dev.in",
        ROOT / "requirements/dev.txt",
    ]
    matching = []
    for path in files:
        if path.exists() and any(line.strip().startswith("arq") for line in path.read_text(encoding="utf-8").splitlines()):
            matching.append(path)
    assert matching, "arq must be pinned in at least one canonical requirements file"


def test_jobs_module_imports_without_arq_import_error():
    module = importlib.import_module("app.modules.jobs")
    assert hasattr(module, "WorkerSettings")


def test_worker_settings_exposes_consent_reminder_jobs():
    module = importlib.import_module("app.modules.jobs")
    functions = getattr(module.WorkerSettings, "functions", [])
    names = {getattr(function, "__name__", str(function)) for function in functions}
    assert "send_consent_reminders" in names or hasattr(module, "send_consent_reminders")
    assert "send_consent_renewal_reminders" in names or hasattr(module, "send_consent_renewal_reminders")
    assert "generate_lesson_job" in names or hasattr(module, "generate_lesson_job")
    assert "generate_study_plan_job" in names or hasattr(module, "generate_study_plan_job")
    assert "run_practice_session_cleanup" in names or hasattr(module, "run_practice_session_cleanup")


def test_jobs_use_dependency_factory_for_consent_reminders():
    source = (ROOT / "app/modules/jobs.py").read_text(encoding="utf-8")
    assert "run_consent_reminder_cycle" in source
    assert "job_dependency_factory" in source
    assert "ConsentService(" not in source


def test_arq_import_compat_reports_status():
    compat = importlib.import_module("app.services.arq_import_compat")
    status = compat.arq_dependency_status()
    assert "available" in status
    assert "import_error" in status
    assert hasattr(compat, "RedisSettings")
    assert hasattr(compat, "cron")
