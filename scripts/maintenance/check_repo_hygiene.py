#!/usr/bin/env python3
"""Repository hygiene checks for root clutter and tracked generated artifacts."""

from __future__ import annotations

import fnmatch
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT_ALLOWED_FILES = {
    '.agent.md',
    '.coveragerc',
    '.dockerignore',
    '.env.example',
    '.env.supabase.example',
    '.gitattributes',
    '.gitignore',
    '.gitleaks.toml',
    '.importlinter',
    '.pre-commit-config.yaml',
    '.python-version',
    '.secrets.baseline',
    'CHANGELOG.md',
    'CODE_OF_CONDUCT.md',
    'CONTRIBUTING.md',
    'AGENT_INSTRUCTIONS_V2.md',
    'LICENSE',
    'Makefile',
    'Makefile.arch',
    'Memory.md',
    'PRIVACY_NOTICE.md',
    'README.md',
    'SECURITY.md',
    'TODO.md',
    'alembic.ini',
    'docker-compose.content-factory-test.yml',
    'docker-compose.override.example.yml',
    'docker-compose.prod.yml',
    'docker-compose.v2.yml',
    'docker-compose.yml',
    'mkdocs.yml',
    'package-lock.json',
    'package.json',
    'pnpm-lock.yaml',
    'openapi.json',
    'openapi.yaml',
    'playwright.config.ts',
    'prometheus.yml',
    'pyproject.toml',
    'pytest-coverage.ini',
    'pytest.ini',
    'render.yaml',
    'requirements-dev.txt',
    'requirements-docs.txt',
    'requirements-ml.txt',
    'requirements.txt',
    'skills-lock.json',
}

ROOT_GENERATED_DOCS = {
    'docs_gap_report.md',
    'docs_generation_plan.md',
    'docs_inventory.json',
    'docs_inventory.md',
}

TRACKED_NOISE_PATTERNS = (
    '.coverage',
    'coverage.xml',
    'htmlcov/*',
    '.pytest_cache/*',
    '.ruff_cache/*',
    '.mypy_cache/*',
    '.import_linter_cache/*',
    '.venv/*',
    'node_modules/*',
    'app/frontend/node_modules/*',
    'dist/*',
    'build/*',
    '*__pycache__*',
    '*.pyc',
)

@dataclass(frozen=True)
class HygieneFailure:
    code: str
    path: str
    detail: str


def _git_ls_files(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ['git', 'ls-files'],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def _matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def run_checks(repo_root: Path | None = None) -> list[HygieneFailure]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    tracked = _git_ls_files(repo_root)
    failures: list[HygieneFailure] = []

    for path in tracked:
        if '/' not in path:
            if path in ROOT_GENERATED_DOCS:
                failures.append(
                    HygieneFailure(
                        'ROOT_GENERATED_DOC',
                        path,
                        'generated documentation intelligence belongs in docs/generated/documentation_intelligence/',
                    )
                )
            elif path not in ROOT_ALLOWED_FILES:
                failures.append(
                    HygieneFailure(
                        'ROOT_CLUTTER',
                        path,
                        'tracked root file is outside the repository root allowlist',
                    )
                )

        if _matches_any(path, TRACKED_NOISE_PATTERNS):
            failures.append(
                HygieneFailure(
                    'TRACKED_GENERATED_NOISE',
                    path,
                    'coverage/cache/build artifacts must not be tracked',
                )
            )

    return failures


def main() -> int:
    failures = run_checks()
    if not failures:
        print('Repository hygiene check passed.')
        return 0

    print('Repository hygiene check failed:')
    for failure in failures:
        print(f'- [{failure.code}] {failure.path}: {failure.detail}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
