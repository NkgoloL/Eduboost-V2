#!/usr/bin/env python3
"""Static checks for warning-cleanup guardrails."""
from __future__ import annotations

from pathlib import Path
import re


REQUIRED_NORECURSEDIRS = {".hypothesis", ".pytest_cache", "tests/legacy", ".venv", "venv", "node_modules"}


def _pytest_norecursedirs() -> set[str]:
    text = Path("pytest.ini").read_text(encoding="utf-8")
    match = re.search(r"^norecursedirs\s*=\s*(?P<value>.+)$", text, flags=re.MULTILINE)
    if not match:
        return set()
    return set(match.group("value").split())


def _mock_session_blocks(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"def _mock_session\(self\):\n(?P<body>(?:        .*\n)+?)        return (?P<var>\w+)\n",
        flags=re.MULTILINE,
    )
    return [match.group(0) for match in pattern.finditer(text)]


def main() -> int:
    failures: list[str] = []
    print("Warning cleanup static check")

    observed = _pytest_norecursedirs()
    missing = REQUIRED_NORECURSEDIRS - observed
    if missing:
        failures.append("pytest.ini norecursedirs missing: " + ", ".join(sorted(missing)))
        print("- FAIL [pytest.ini] missing norecursedirs: " + ", ".join(sorted(missing)))
    else:
        print("- PASS [pytest.ini] default-style norecursedirs restored")

    repo_test = Path("tests/unit/test_v2_repositories_full.py")
    if repo_test.exists():
        for idx, block in enumerate(_mock_session_blocks(repo_test), start=1):
            if ".add = MagicMock()" not in block:
                failures.append(f"{repo_test} _mock_session block {idx} lacks synchronous add MagicMock")
        if not any(f.startswith(str(repo_test)) for f in failures):
            print(f"- PASS [{repo_test}] _mock_session blocks define synchronous add")
    else:
        failures.append(f"missing {repo_test}")

    register = Path("docs/release/warning_cleanup_register.md")
    if register.exists() and "AsyncMock" in register.read_text(encoding="utf-8"):
        print(f"- PASS [{register}] warning register present")
    else:
        failures.append(f"{register} missing or incomplete")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
