"""Run PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7 coverage/static/security gates."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parents[2])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.advisory_suites.coverage_static_security_green import main

if __name__ == "__main__":
    raise SystemExit(main())
