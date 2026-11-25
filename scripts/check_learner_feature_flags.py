#!/usr/bin/env python3
"""Fail CI if a deployment enables learner diagnostics/mastery without pilot authorization."""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "docker-compose.yml", ROOT / "docker-compose.v2.yml", ROOT / "docker-compose.prod.yml",
    ROOT / "render.yaml", ROOT / "deployment", ROOT / "bicep", ROOT / "k8s",
]
FEATURES = ("LEARNER_DIAGNOSTIC_ENABLED", "LEARNER_MASTERY_VIEW_ENABLED")
TRUE = re.compile(r"(?i)(?:^|[=:]\s*|-\s*)(?:true|1|yes|on)(?:\s|$|#)")

def files():
    for target in TARGETS:
        if target.is_file():
            yield target
        elif target.is_dir():
            yield from (p for p in target.rglob("*") if p.is_file() and p.suffix.lower() in {".yml", ".yaml", ".json", ".bicep", ".env"})

def enabled(text: str, key: str) -> bool:
    for line in text.splitlines():
        if key not in line or "secrets." in line or "vars." in line:
            continue
        if TRUE.search(line.split(key, 1)[1]):
            return True
    return False

def main() -> int:
    errors = []
    for path in files():
        text = path.read_text(encoding="utf-8", errors="replace")
        authorized = enabled(text, "LEARNER_PILOT_AUTHORIZATION")
        for feature in FEATURES:
            if enabled(text, feature) and not authorized:
                errors.append(f"{path.relative_to(ROOT)} enables {feature} without LEARNER_PILOT_AUTHORIZATION=true")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Learner diagnostic/mastery deployment flags are fail-closed or pilot-authorized.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
