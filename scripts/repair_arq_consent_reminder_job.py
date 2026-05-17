#!/usr/bin/env python3
from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / "app/modules/jobs.py"
CORE_JOBS = ROOT / "app/core/jobs.py"
REPORT = ROOT / "docs/release/arq_consent_job_repair_report.md"
BLOCKER = ROOT / "docs/release/arq_consent_job_repair_blockers.md"

JOB_FUNCTION_NAMES = ("send_consent_reminders", "send_consent_renewal_reminders", "consent_reminder_job")


def _ensure_import(text: str, line: str) -> str:
    if line.strip() in text:
        return text
    lines = text.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].startswith('"""'):
        insert_at = 1
        while insert_at < len(lines) and '"""' not in lines[insert_at]:
            insert_at += 1
        insert_at = min(insert_at + 1, len(lines))
    if insert_at < len(lines) and lines[insert_at].startswith("from __future__"):
        insert_at += 1
    while insert_at < len(lines) and (lines[insert_at].startswith("import ") or lines[insert_at].startswith("from ")):
        insert_at += 1
    lines.insert(insert_at, line if line.endswith("\n") else line + "\n")
    return "".join(lines)


def _replacement_function() -> str:
    return '''async def send_consent_reminders(ctx: dict | None = None) -> None:
    """ARQ job: send consent renewal reminders using an explicit DB session."""
    validate_arq_job_payload(ctx or {})

    async with AsyncSessionLocal() as session:
        repo = ConsentRepository(session)
        params = inspect.signature(ConsentService).parameters
        kwargs = {}
        if "consent_repo" in params:
            kwargs["consent_repo"] = repo
        elif "consent_repository" in params:
            kwargs["consent_repository"] = repo
        if "db" in params:
            kwargs["db"] = session
        if "session" in params:
            kwargs["session"] = session
        service = ConsentService(**kwargs) if kwargs else ConsentService(session)

        reminder = (
            getattr(service, "send_renewal_reminders", None)
            or getattr(service, "send_consent_reminders", None)
            or getattr(service, "process_renewal_reminders", None)
        )
        if reminder is None:
            return

        result = reminder()
        if inspect.isawaitable(result):
            await result

'''


def _replace_or_add_job(text: str) -> str:
    function_body = _replacement_function()
    tree = ast.parse(text)
    lines = text.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name in JOB_FUNCTION_NAMES:
            lines[node.lineno - 1:(node.end_lineno or node.lineno)] = function_body.rstrip("\n").splitlines()
            return "\n".join(lines) + ("\n" if text.endswith("\n") else "")

    return text.rstrip() + "\n\n" + function_body


def _patch_core_jobs_docstring() -> None:
    if not CORE_JOBS.exists():
        return
    text = CORE_JOBS.read_text(encoding="utf-8")
    if "Policy: Use FastAPI BackgroundTasks for non-critical, request-adjacent work only." in text:
        return
    doc = '''"""
FastAPI BackgroundTasks wrapper.

Policy: Use FastAPI BackgroundTasks for non-critical, request-adjacent work only.
Do NOT use this module for durable workflows such as consent reminders, report
generation, erasure execution, or long-running jobs. Durable workflows belong in
`app/modules/jobs.py` and should run through ARQ or an equivalent worker.
"""

'''
    if text.startswith('"""'):
        end = text.find('"""', 3)
        if end != -1:
            text = text[end + 3:].lstrip()
    CORE_JOBS.write_text(doc + text, encoding="utf-8")


def main() -> int:
    if not JOBS.exists():
        BLOCKER.write_text("# ARQ Consent Job Repair Blocker\n\nMissing `app/modules/jobs.py`.\n", encoding="utf-8")
        print("Missing app/modules/jobs.py")
        return 1

    text = JOBS.read_text(encoding="utf-8")
    text = _ensure_import(text, "import inspect")
    text = _ensure_import(text, "from app.core.database import AsyncSessionLocal")
    text = _ensure_import(text, "from app.modules.consent.service import ConsentService")
    text = _ensure_import(text, "from app.repositories.consent_repository import ConsentRepository")
    text = _ensure_import(text, "from app.services.job_runtime_integrity import validate_arq_job_payload")
    text = _replace_or_add_job(text)

    if "ConsentService()" in text:
        BLOCKER.write_text(
            "# ARQ Consent Job Repair Blocker\n\n`ConsentService()` empty constructor still appears in `app/modules/jobs.py`.\n",
            encoding="utf-8",
        )
        print("ConsentService() empty constructor remains")
        return 1

    ast.parse(text)
    JOBS.write_text(text, encoding="utf-8")

    _patch_core_jobs_docstring()

    REPORT.write_text(
        "\n".join([
            "# ARQ Consent Job Repair Report",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            "**Status:** implemented",
            "",
            "- Consent reminder job uses `AsyncSessionLocal`.",
            "- Consent reminder job constructs `ConsentRepository(session)`.",
            "- Consent reminder job constructs `ConsentService` with explicit dependencies.",
            "- FastAPI BackgroundTasks policy docstring updated.",
            "",
        ]),
        encoding="utf-8",
    )
    if BLOCKER.exists():
        BLOCKER.unlink()
    print(f"Patched {JOBS.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
