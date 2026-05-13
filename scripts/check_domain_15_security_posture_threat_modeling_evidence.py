#!/usr/bin/env python3
"""Domain 15 evidence wrapper for security posture and threat modeling."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_security_posture_threat_modeling_production_readiness import main

if __name__ == "__main__":
    raise SystemExit(main())
