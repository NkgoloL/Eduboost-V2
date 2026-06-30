#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTICS = ROOT / "app/api_v2_routers/diagnostics.py"
REPORT = ROOT / "docs/release/diagnostics_dynamic_repository_boundary_repair_report.md"

BOUNDARY_IMPORT = "from app.api_v2_deps import diagnostic_repositories\n"

# Direct repository constructor/proxy calls that have appeared across the recent
# refactors. These are replaced with an explicit dependency-boundary call.
CALL_REPLACEMENTS = {
    "LearnerRepository(db)": "diagnostic_repositories.learner(db)",
    "GuardianRepository(db)": "diagnostic_repositories.guardian(db)",
    "IRTRepository(db)": "diagnostic_repositories.irt(db)",
    "DiagnosticRepository(db)": "diagnostic_repositories.diagnostic(db)",
    "KnowledgeGapRepository(db)": "diagnostic_repositories.knowledge_gap(db)",
    "ItemBankRepository(db)": "diagnostic_repositories.item_bank(db)",
    "DiagnosticSessionRepository(db)": "diagnostic_repositories.diagnostic_session(db)",
    "MasteryRepository(db)": "diagnostic_repositories.mastery(db)",
    "_LearnerRepo(db)": "diagnostic_repositories.learner(db)",
    "_GuardianRepo(db)": "diagnostic_repositories.guardian(db)",
    "_IRTRepo(db)": "diagnostic_repositories.irt(db)",
    "_DiagnosticRepo(db)": "diagnostic_repositories.diagnostic(db)",
    "_KnowledgeGapRepo(db)": "diagnostic_repositories.knowledge_gap(db)",
    "_ItemBankRepo(db)": "diagnostic_repositories.item_bank(db)",
    "_DiagnosticSessionRepo(db)": "diagnostic_repositories.diagnostic_session(db)",
    "_MasteryRepo(db)": "diagnostic_repositories.mastery(db)",
}

BLOCK_REPOSITORY_IMPORT_RE = re.compile(
    r"\nfrom app\.repositories\.repositories import \(.*?\)\n",
    re.DOTALL,
)
SINGLE_REPOSITORY_IMPORT_RE = re.compile(
    r"^from app\.repositories(?:\.[\w_]+)* import .*\n",
    re.MULTILINE,
)


def _line_ranges_to_remove(tree: ast.AST, lines: list[str]) -> set[int]:
    remove: set[int] = set()
    for node in getattr(tree, "body", []):
        start = getattr(node, "lineno", None)
        end = getattr(node, "end_lineno", None)
        if start is None or end is None:
            continue
        source = "".join(lines[start - 1 : end])
        node_name = getattr(node, "name", "")

        should_remove = False
        if isinstance(node, ast.Import):
            should_remove = any(alias.name == "importlib" for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            should_remove = bool(node.module and node.module.startswith("app.repositories"))
        elif "importlib.import_module" in source or "app.repositories" in source:
            # Remove local dynamic repository proxy definitions or assignments.
            # Keep ordinary route functions unless they only contain dynamic proxy setup.
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                should_remove = (
                    node_name.startswith("_")
                    or "Repo" in node_name
                    or "Repository" in node_name
                    or "resolve" in node_name.lower()
                )
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                should_remove = True

        if should_remove:
            remove.update(range(start, end + 1))
    return remove


def _remove_dynamic_proxy_blocks(text: str) -> str:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return text
    lines = text.splitlines(keepends=True)
    remove = _line_ranges_to_remove(tree, lines)
    if not remove:
        return text
    kept = [line for index, line in enumerate(lines, start=1) if index not in remove]
    return "".join(kept)


def _ensure_boundary_import(text: str) -> str:
    if BOUNDARY_IMPORT.strip() in text:
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
        lines[insert_at].startswith("import ") or lines[insert_at].startswith("from ") or lines[insert_at].strip() == ""
    ):
        insert_at += 1
    lines.insert(insert_at, BOUNDARY_IMPORT)
    return "".join(lines)


def patch_diagnostics() -> bool:
    text = DIAGNOSTICS.read_text(encoding="utf-8")
    original = text

    # Replace constructor/proxy calls first so route bodies no longer need repository symbols.
    for old, new in CALL_REPLACEMENTS.items():
        text = text.replace(old, new)

    # Remove direct repository imports in both block and single-line forms.
    text = BLOCK_REPOSITORY_IMPORT_RE.sub("\n", text)
    text = SINGLE_REPOSITORY_IMPORT_RE.sub("", text)

    # Remove top-level dynamic proxy definitions left by the prior static-scan bypass.
    text = _remove_dynamic_proxy_blocks(text)

    # Remove an importlib import if it survived and the router no longer needs it.
    text = re.sub(r"^import importlib\n", "", text, flags=re.MULTILINE)

    text = _ensure_boundary_import(text)

    # Normalize excessive blank lines introduced by block removal.
    text = re.sub(r"\n{3,}", "\n\n", text)

    ast.parse(text)
    if text != original:
        DIAGNOSTICS.write_text(text, encoding="utf-8")
        changed = True
    else:
        changed = False

    REPORT.write_text(
        "\n".join(
            [
                "# Diagnostics Dynamic Repository Boundary Repair Report",
                "",
                f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
                "",
                "**Status:** implemented",
                "",
                f"- diagnostics.py patched: `{changed}`",
                "- Dynamic repository resolution moved to `app/api_v2_deps/diagnostic_repositories.py`.",
                "- diagnostics.py now calls the dependency boundary instead of resolving repositories itself.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return changed


def main() -> int:
    patch_diagnostics()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
