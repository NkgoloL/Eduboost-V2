#!/usr/bin/env python3
"""Guard prompt-bearing string literals against explicit secret markers.

The guard intentionally does not fail on normal configuration code that references
secret names such as ANTHROPIC_API_KEY or AZURE_KEY_VAULT_URL. It only fails when
a prompt-like string literal itself embeds a secret-bearing identifier.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = (
    REPO_ROOT / "app",
    REPO_ROOT / "services",
)

PROMPT_MARKERS = (
    "prompt",
    "system_message",
    "user_message",
    "generate_lesson",
    "diagnostic",
    "remediation",
    "lesson",
)

SECRET_MARKERS = (
    "JWT_SECRET",
    "JWT_SECRET_KEY",
    "ENCRYPTION_KEY",
    "ENCRYPTION_SALT",
    "BACKUP_ENCRYPTION_KEY",
    "GROQ_API_KEY",
    "ANTHROPIC_API_KEY",
    "AZURE_STORAGE_CONNECTION_STRING",
    "AZURE_KEY_VAULT_URL",
)


@dataclass(frozen=True)
class PromptSecretLeakageResult:
    path: str
    ok: bool
    detail: str


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if root.exists():
            files.extend(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)
    return sorted(set(files))


def _string_literals(path: Path) -> list[tuple[int, str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return []

    literals: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.append((getattr(node, "lineno", 0), node.value))
        elif isinstance(node, ast.JoinedStr):
            text_parts: list[str] = []
            for value in node.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    text_parts.append(value.value)
            if text_parts:
                literals.append((getattr(node, "lineno", 0), "".join(text_parts)))
    return literals


def _is_prompt_literal(value: str) -> bool:
    lowered = value.lower()
    return any(marker.lower() in lowered for marker in PROMPT_MARKERS)


def run_checks() -> list[PromptSecretLeakageResult]:
    results: list[PromptSecretLeakageResult] = []
    scanned_prompt_literals = 0

    for path in _iter_python_files():
        rel_path = str(path.relative_to(REPO_ROOT))
        for lineno, literal in _string_literals(path):
            if not _is_prompt_literal(literal):
                continue

            scanned_prompt_literals += 1
            for marker in SECRET_MARKERS:
                results.append(
                    PromptSecretLeakageResult(
                        f"{rel_path}:{lineno}",
                        marker not in literal,
                        f"prompt literal does not embed {marker}"
                        if marker not in literal
                        else f"prompt literal embeds secret marker {marker}",
                    )
                )

    results.append(
        PromptSecretLeakageResult(
            "prompt literals",
            True,
            f"scanned {scanned_prompt_literals} prompt-bearing string literals",
        )
    )
    return results


def main() -> int:
    results = run_checks()
    print("AI prompt secret leakage check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.path}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
