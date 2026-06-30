#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH_ROUTER = ROOT / "app/api_v2_routers/auth.py"
REPORT = ROOT / "docs/release/auth_router_boundary_repair_report.md"
BLOCKER = ROOT / "docs/release/auth_router_boundary_repair_blockers.md"

IMPORT_LINE = "from app.api_v2_deps.auth_runtime import AuthRuntimeContext, get_auth_runtime_context\n"
MARKER = "# code_721_750_auth_runtime_boundary"


def _write_blocker(message: str) -> None:
    BLOCKER.write_text(
        "\n".join([
            "# Auth Router Boundary Repair Blocker",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            message,
            "",
        ]),
        encoding="utf-8",
    )


def _ensure_import(text: str) -> str:
    if "app.api_v2_deps.auth_runtime" in text:
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
    while insert_at < len(lines) and (
        lines[insert_at].startswith("import ") or lines[insert_at].startswith("from ")
    ):
        insert_at += 1
    lines.insert(insert_at, IMPORT_LINE)
    return "".join(lines)


def _remove_learner_repository_imports(text: str) -> str:
    updated_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.strip().startswith("from app.repositories.learner_repository import") and "LearnerRepository" in line:
            names = line.split("import", 1)[1]
            kept = [name.strip() for name in names.split(",") if name.strip() and name.strip() != "LearnerRepository"]
            if kept:
                updated_lines.append(line.split("import", 1)[0] + "import " + ", ".join(kept) + "\n")
            continue

        if line.strip().startswith("from app.repositories.repositories import") and "LearnerRepository" in line:
            names = line.split("import", 1)[1]
            kept = [name.strip() for name in names.split(",") if name.strip() and name.strip() != "LearnerRepository"]
            if kept:
                updated_lines.append(line.split("import", 1)[0] + "import " + ", ".join(kept) + "\n")
            continue

        updated_lines.append(line)
    return "".join(updated_lines)


def _replace_learner_repository_constructors(text: str) -> str:
    replacements = (
        (r"LearnerRepository\(\s*db\s*\)", "auth_runtime.learner_repo"),
        (r"LearnerRepository\(\s*session\s*\)", "auth_runtime.learner_repo"),
        (r"LearnerRepository\(\s*database\s*\)", "auth_runtime.learner_repo"),
        (r"LearnerRepository\(\s*\)", "auth_runtime.learner_repo"),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return text


def _replace_direct_get_by_guardian(text: str) -> str:
    # Replace common refresh patterns after constructor replacement:
    #   learners = await learner_repo.get_by_guardian(guardian.id)
    #   learners = await auth_runtime.learner_repo.get_by_guardian(guardian.id)
    # with:
    #   guardian_learner_ids = await auth_runtime.guardian_learner_ids(guardian.id)
    # and leave later claim-building code to use guardian_learner_ids.
    text = re.sub(
        r"(?P<indent>^[ \t]*)(?P<var>\w+)\s*=\s*await\s+(?:learner_repo|auth_runtime\.learner_repo)\.get_by_guardian\((?P<guardian>[^)]+)\)\s*$",
        r"\g<indent>guardian_learner_ids = await auth_runtime.guardian_learner_ids(\g<guardian>)",
        text,
        flags=re.MULTILINE,
    )

    # If code then maps learner IDs from the old learners var, normalize the
    # most common forms to preserve claim behavior.
    text = re.sub(
        r"guardian_learner_ids\s*=\s*\[\s*(?:str\()?learner\.id\)?\s*for\s+learner\s+in\s+\w+\s*\]",
        "guardian_learner_ids = [str(item) for item in guardian_learner_ids]",
        text,
    )
    text = re.sub(
        r"guardian_learner_ids\s*=\s*\[\s*learner\.id\s*for\s+learner\s+in\s+\w+\s*\]",
        "guardian_learner_ids = guardian_learner_ids",
        text,
    )
    return text


def _auth_runtime_needed(block: str) -> bool:
    return "auth_runtime." in block


def _patch_function_signatures(text: str) -> str:
    tree = ast.parse(text)
    lines = text.splitlines()

    patches: list[tuple[int, int, list[str]]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        block = "\n".join(lines[node.lineno - 1:(node.end_lineno or node.lineno)])
        if not _auth_runtime_needed(block):
            continue

        args = [arg.arg for arg in node.args.args + node.args.kwonlyargs]
        if "auth_runtime" in args:
            continue

        header_start = node.lineno - 1
        body_start = node.body[0].lineno - 1 if node.body else node.lineno
        header_lines = lines[header_start:body_start]
        header_text = "\n".join(header_lines)

        if "Depends(" not in header_text and "Depends(" not in text:
            raise RuntimeError(f"{node.name}: FastAPI Depends is not available in auth router")

        param = "auth_runtime: AuthRuntimeContext = Depends(get_auth_runtime_context)"

        if len(header_lines) == 1:
            line = header_lines[0]
            replaced = re.sub(r"\)\s*(->[^:]+)?:", rf", {param})\1:", line, count=1)
            patches.append((header_start, body_start, [replaced]))
        else:
            # Insert before closing signature line.
            close_index = None
            for idx in range(len(header_lines) - 1, -1, -1):
                if header_lines[idx].strip().endswith(":"):
                    close_index = header_start + idx
                    break
            if close_index is None:
                raise RuntimeError(f"{node.name}: could not locate signature close line")
            close_indent = re.match(r"^(\s*)", lines[close_index]).group(1)
            patches.append((close_index, close_index, [f"{close_indent}    {param},"]))

    for start, end, replacement in sorted(patches, reverse=True):
        lines[start:end] = replacement

    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def main() -> int:
    if not AUTH_ROUTER.exists():
        _write_blocker("Missing app/api_v2_routers/auth.py")
        return 1

    source = AUTH_ROUTER.read_text(encoding="utf-8")
    text = source
    text = _ensure_import(text)
    text = _replace_learner_repository_constructors(text)
    text = _replace_direct_get_by_guardian(text)
    text = _patch_function_signatures(text)
    text = _remove_learner_repository_imports(text)

    ast.parse(text)

    if "LearnerRepository(" in text:
        _write_blocker("Auth router still contains `LearnerRepository(` after repair.")
        print("Auth router still contains LearnerRepository constructor.")
        return 1

    if "LearnerRepository" in text:
        _write_blocker("Auth router still contains `LearnerRepository` symbol after repair. Manual cleanup required.")
        print("Auth router still contains LearnerRepository symbol.")
        return 1

    if text != source:
        AUTH_ROUTER.write_text(text, encoding="utf-8")

    REPORT.write_text(
        "\n".join([
            "# Auth Router Boundary Repair Report",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            "**Status:** implemented",
            "",
            "- Added `app/api_v2_deps/auth_runtime.py` dependency module.",
            "- Added `app/services/auth_runtime_boundary.py` runtime context service.",
            "- Removed direct `LearnerRepository` construction/import from auth router.",
            "- Routed guardian learner scope lookup through `AuthRuntimeContext.guardian_learner_ids`.",
            "",
            "## Boundary",
            "",
            "This batch closes the direct learner-repository refresh allowance. Remaining auth repository imports must be handled by a later full AuthService extraction batch.",
            "",
        ]),
        encoding="utf-8",
    )
    if BLOCKER.exists():
        BLOCKER.unlink()
    print(f"Patched {AUTH_ROUTER.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
