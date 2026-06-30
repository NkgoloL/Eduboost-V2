#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/release/runtime_blocker_repair_after_followup_audit.md"


def _ensure_import(text: str, import_line: str) -> str:
    module_part = import_line.split(" import ", 1)[0].replace("from ", "")
    if import_line.strip() in text or module_part in text:
        return text
    lines = text.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].startswith('\"\"\"'):
        insert_at = 1
        while insert_at < len(lines) and '\"\"\"' not in lines[insert_at]:
            insert_at += 1
        insert_at = min(insert_at + 1, len(lines))
    if insert_at < len(lines) and lines[insert_at].startswith("from __future__"):
        insert_at += 1
    while insert_at < len(lines) and (lines[insert_at].startswith("import ") or lines[insert_at].startswith("from ")):
        insert_at += 1
    lines.insert(insert_at, import_line if import_line.endswith("\n") else import_line + "\n")
    return "".join(lines)


def patch_consent_dependency() -> list[str]:
    path = ROOT / "app/api_v2_deps/consent_lifecycle.py"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    original = text
    text = _ensure_import(text, "from app.services.popia_consent_lifecycle_adapter import POPIAConsentLifecycleAdapter")
    replacements = {
        "return ConsentService(session=db)": "return POPIAConsentLifecycleAdapter(ConsentService(session=db))",
        "return ConsentService(db=db)": "return POPIAConsentLifecycleAdapter(ConsentService(db=db))",
        "return ConsentService(consent_repository=repo)": "return POPIAConsentLifecycleAdapter(ConsentService(consent_repository=repo))",
        "return ConsentService(consent_repo=repo)": "return POPIAConsentLifecycleAdapter(ConsentService(consent_repo=repo))",
        "return ConsentService(db)": "return POPIAConsentLifecycleAdapter(ConsentService(db))",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    ast.parse(text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return [str(path.relative_to(ROOT))]
    return []


def patch_auth_runtime_boundary() -> list[str]:
    path = ROOT / "app/services/auth_runtime_boundary.py"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    original = text
    if "consent_repo:" not in text:
        text = text.replace(
            "learner_repo: Any | None = None\n",
            "learner_repo: Any | None = None\n    consent_repo: Any | None = None\n    guardian_repo: Any | None = None\n",
        )
    if "consent_repo_cls" not in text:
        text = text.replace(
            "learner_repo = _construct_repository(learner_repo_cls, db) if learner_repo_cls is not None else None\n    return AuthRuntimeContext(db=db, learner_repo=learner_repo)",
            "consent_repo_cls = (\n        _import_symbol(\"app.repositories.consent_repository.ConsentRepository\")\n        or _import_symbol(\"app.repositories.repositories.ConsentRepository\")\n    )\n    guardian_repo_cls = (\n        _import_symbol(\"app.repositories.guardian_repository.GuardianRepository\")\n        or _import_symbol(\"app.repositories.repositories.GuardianRepository\")\n    )\n    learner_repo = _construct_repository(learner_repo_cls, db) if learner_repo_cls is not None else None\n    consent_repo = _construct_repository(consent_repo_cls, db) if consent_repo_cls is not None else None\n    guardian_repo = _construct_repository(guardian_repo_cls, db) if guardian_repo_cls is not None else None\n    return AuthRuntimeContext(db=db, learner_repo=learner_repo, consent_repo=consent_repo, guardian_repo=guardian_repo)",
        )
    ast.parse(text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return [str(path.relative_to(ROOT))]
    return []


def patch_auth_router() -> list[str]:
    path = ROOT / "app/api_v2_routers/auth.py"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    original = text
    text = _ensure_import(text, "from app.api_v2_deps.auth_runtime import AuthRuntimeContext, get_auth_runtime_context")
    text = re.sub(r"ConsentRepository\(\s*(?:db|session|database)\s*\)", "auth_runtime.consent_repo", text)
    text = re.sub(r"GuardianRepository\(\s*(?:db|session|database)\s*\)", "auth_runtime.guardian_repo", text)
    text = re.sub(r"guardian_learner_ids\s*=\s*\[[^\]\n]*for\s+\w+\s+in\s+learners[^\]\n]*\]", "guardian_learner_ids = [str(item) for item in guardian_learner_ids]", text)
    text = re.sub(r"\bif learners:\n(\s*)", r"if guardian_learner_ids:\n\1", text)
    for repo_name in ("ConsentRepository", "GuardianRepository", "LearnerRepository"):
        lines = []
        for line in text.splitlines(keepends=True):
            if line.strip().startswith("from app.repositories") and repo_name in line:
                names = line.split("import", 1)[1]
                kept = [name.strip() for name in names.split(",") if name.strip() and name.strip() != repo_name]
                if kept:
                    lines.append(line.split("import", 1)[0] + "import " + ", ".join(kept) + "\n")
                continue
            lines.append(line)
        text = "".join(lines)
    ast.parse(text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return [str(path.relative_to(ROOT))]
    return []


def patch_diagnostics() -> list[str]:
    path = ROOT / "app/api_v2_routers/diagnostics.py"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    original = text.replace("require_items=False", "require_items=True")
    if original != text:
        ast.parse(original)
        path.write_text(original, encoding="utf-8")
        return [str(path.relative_to(ROOT))]
    return []


def patch_jobs() -> list[str]:
    path = ROOT / "app/modules/jobs.py"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    original = text
    text = _ensure_import(text, "from app.services.job_dependency_factory import run_consent_reminder_cycle")
    text = _ensure_import(text, "from app.services.job_runtime_integrity import validate_arq_job_payload")
    replacement_block = "\n".join([
        "# code_781_830R_durable_consent_job_compat",
        "async def send_consent_reminders(ctx: dict | None = None) -> None:",
        "    validate_arq_job_payload(ctx or {})",
        "    await run_consent_reminder_cycle(ctx or {})",
        "",
        "",
        "async def send_consent_renewal_reminders(ctx: dict | None = None) -> None:",
        "    validate_arq_job_payload(ctx or {})",
        "    await run_consent_reminder_cycle(ctx or {})",
        "",
    ])
    tree = ast.parse(text)
    lines = text.splitlines()
    ranges = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name in {"send_consent_reminders", "send_consent_renewal_reminders"}:
            ranges.append((node.lineno - 1, node.end_lineno or node.lineno))
    for start, end in sorted(ranges, reverse=True):
        lines[start:end] = []
    text = "\n".join(lines).rstrip() + "\n\n" + replacement_block
    new_lines = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("from app.core.database import AsyncSessionLocal"):
            continue
        if stripped.startswith("from app.modules.consent.service import ConsentService"):
            continue
        if stripped.startswith("from app.repositories") and any(name in line for name in ("ConsentRepository", "AuditRepository")):
            continue
        new_lines.append(line)
    text = "".join(new_lines)
    ast.parse(text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return [str(path.relative_to(ROOT))]
    return []


def main() -> int:
    changed: list[str] = []
    changed += patch_consent_dependency()
    changed += patch_auth_runtime_boundary()
    changed += patch_auth_router()
    changed += patch_diagnostics()
    changed += patch_jobs()
    REPORT.write_text("\n".join([
        "# Runtime Blocker Repair After Follow-up Audit",
        "",
        f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        "",
        "**Status:** implemented",
        "",
        "## Patched files",
        "",
        *(f"- `{item}`" for item in changed),
        "",
        "## Remaining debt",
        "",
        "- POPIA lifecycle still needs endpoint integration tests.",
        "- Diagnostics served-item/session CAPS binding still needs real DB tests.",
        "- Full AuthService extraction remains queued.",
        "- Live ARQ worker smoke remains required.",
        "",
    ]), encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    for item in changed:
        print(f"Patched {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
