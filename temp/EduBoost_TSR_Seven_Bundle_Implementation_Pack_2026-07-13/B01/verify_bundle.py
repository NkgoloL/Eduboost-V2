#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--repo", default=".")
    p.add_argument("--skip-heavy", action="store_true")
    a=p.parse_args()
    repo=Path(a.repo).resolve()
    cmd=[sys.executable, "-m", "scripts.true_state_remediation.execute_bundle", "--repo", str(repo), "--bundle", "B01", "--phase", "verify", "--json"]
    if a.skip_heavy: cmd.append("--skip-heavy")
    return subprocess.run(cmd, cwd=repo, check=False).returncode
if __name__ == "__main__": raise SystemExit(main())
