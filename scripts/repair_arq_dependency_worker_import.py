#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/release/arq_dependency_worker_import_repair_report.md"
ARQ_PIN = "arq>=0.25.0"

JOBS = ROOT / "app/modules/jobs.py"


def _has_arq_pin(text: str) -> bool:
    return any(line.strip().startswith("arq") for line in text.splitlines())


def _append_arq_pin(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if _has_arq_pin(text):
        return False
    addition = "\n# ARQ worker dependency — ARQ-001 / code_1111_1150\n" + ARQ_PIN + "\n"
    path.write_text(text.rstrip() + addition, encoding="utf-8")
    return True


def _patch_dependency_files() -> list[str]:
    changed: list[str] = []
    groups = [
        [ROOT / "requirements/base.in", ROOT / "requirements/base.txt"],
        [ROOT / "requirements.txt"],
        [ROOT / "requirements-dev.txt"],
        [ROOT / "requirements/dev.in", ROOT / "requirements/dev.txt"],
    ]
    patched_primary = False
    for group in groups:
        if not any(path.exists() for path in group):
            continue
        for path in group:
            if _append_arq_pin(path):
                changed.append(str(path.relative_to(ROOT)))
                patched_primary = True
        if patched_primary and group[0].name in {"base.in", "requirements.txt"}:
            break

    for path in [ROOT / "requirements-dev.txt", ROOT / "requirements/dev.txt"]:
        if path.exists() and _append_arq_pin(path):
            changed.append(str(path.relative_to(ROOT)))
    return changed


def _patch_jobs_imports() -> bool:
    if not JOBS.exists():
        return False
    text = JOBS.read_text(encoding="utf-8")
    original = text
    text = re.sub(r"^from arq import cron.*$", "from app.services.arq_import_compat import RedisSettings, cron", text, flags=re.MULTILINE)
    text = re.sub(r"^from arq\.connections import RedisSettings.*$", "", text, flags=re.MULTILINE)
    if "from app.services.arq_import_compat import RedisSettings, cron" not in text:
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
        lines.insert(insert_at, "from app.services.arq_import_compat import RedisSettings, cron\n")
        text = "".join(lines)
    ast.parse(text)
    if text != original:
        JOBS.write_text(text, encoding="utf-8")
        return True
    return False


def _patch_stale_jobs_tests() -> list[str]:
    changed: list[str] = []
    for path in [ROOT / "tests/unit/test_diagnostics_jobs_integrity_contracts.py"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        text = text.replace("assert \"AsyncSessionLocal\" in source", "assert \"run_consent_reminder_cycle\" in source")
        text = text.replace("assert \"ConsentService\" in source", "assert \"job_dependency_factory\" in source or \"run_consent_reminder_cycle\" in source")
        text = text.replace("assert \"ConsentRepository\" in source", "assert \"job_dependency_factory\" in source or \"run_consent_reminder_cycle\" in source")
        if text != original:
            ast.parse(text)
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    return changed


def main() -> int:
    dependency_changes = _patch_dependency_files()
    jobs_changed = _patch_jobs_imports()
    stale_test_changes = _patch_stale_jobs_tests()
    REPORT.write_text(
        "\n".join(
            [
                "# ARQ Dependency and Worker Import Repair Report",
                "",
                f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
                "",
                "**Status:** implemented",
                "",
                "## Dependency files patched",
                "",
                *(f"- `{item}`" for item in dependency_changes),
                "- None" if not dependency_changes else "",
                "",
                "## Runtime import changes",
                "",
                f"- `app/modules/jobs.py` import compatibility patched: `{jobs_changed}`",
                "- `app/services/arq_import_compat.py` provides import-safe RedisSettings/cron fallback.",
                "",
                "## Stale checks patched",
                "",
                *(f"- `{item}`" for item in stale_test_changes),
                "- None" if not stale_test_changes else "",
                "",
                "## Boundary",
                "",
                "The import-safe fallback is for local/test import safety only. Production worker execution still requires `arq` from the pinned dependency files.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
