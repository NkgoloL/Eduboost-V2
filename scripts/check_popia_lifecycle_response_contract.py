#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_popia_response_contract_no_skips import main

if __name__ == "__main__":
    raise SystemExit(main())
