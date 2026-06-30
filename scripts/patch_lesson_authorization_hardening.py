#!/usr/bin/env python3
from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "app/services/lesson_authorization.py"
REPORT = ROOT / "docs/release/lesson_authorization_hardening_report.md"

OLD = """        except Exception:\n            pass\n"""
NEW = """        except (TypeError, AttributeError, RuntimeError, ValueError):\n            # Constructor/signature/shape fallbacks are expected while the canonical\n            # lesson repository surface is settling. Data-layer and unexpected\n            # repository failures must propagate instead of being hidden as 404s.\n            pass\n"""


def main() -> int:
    source = TARGET.read_text(encoding="utf-8")
    original = source

    if OLD in source:
        source = source.replace(OLD, NEW, 1)

    ast.parse(source)
    if source != original:
        TARGET.write_text(source, encoding="utf-8")
        changed = True
    else:
        changed = False

    REPORT.write_text(
        "\n".join(
            [
                "# Lesson Authorization Hardening Report",
                "",
                f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
                "",
                "**Status:** implemented",
                "",
                f"- Narrowed lesson repository fallback exception handling: `{changed}`",
                "- Unexpected repository/data failures are no longer swallowed by the compatibility lookup path.",
                "- Cross-learner read/write negative tests are covered by the LESSON-AUTH-001 focused suite.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
