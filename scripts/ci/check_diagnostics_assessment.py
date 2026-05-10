#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.modules.diagnostics.irt_engine import p_correct_3pl, standard_error_from_information
from types import SimpleNamespace


def main() -> int:
    for theta in [x / 10 for x in range(-40, 41)]:
        p = p_correct_3pl(theta, 1.0, 0.0, 0.25)
        if not 0.25 <= p < 1.0:
            raise SystemExit(f"probability out of range: {p}")
    items = [SimpleNamespace(discrimination_a=1.0, difficulty_b=0.0, guessing_c=0.25)]
    if standard_error_from_information(0.0, items) <= 0:
        raise SystemExit("standard error must be positive")
    print("diagnostics assessment checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
