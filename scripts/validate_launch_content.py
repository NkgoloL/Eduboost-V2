#!/usr/bin/env python3
"""Validate Grade 4 Maths launch content artifacts.

Compatibility wrapper around the generic scope validator.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.curriculum.validate_scope_content import print_result, validate_scope


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Fail if approved artifact counts do not meet configured targets.")
    args = parser.parse_args()

    result = validate_scope("grade4_mathematics_en", strict=args.strict)
    print_result(result)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
