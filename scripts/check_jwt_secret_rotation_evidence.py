#!/usr/bin/env python3
from __future__ import annotations
import ast
import os
import re
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.jwt_secret_rotation_evidence import ACCEPTED_STATUS, write_status  # noqa: E402
CRITICAL = ["scripts/jwt_secret_rotation_evidence.py", "scripts/patch_jwt_secret_rotation_registry.py", "scripts/check_jwt_secret_rotation_evidence.py", "tests/unit/test_jwt_secret_rotation_evidence.py"]

def read(p: str) -> str: return (ROOT / p).read_text(encoding="utf-8")
def entry(text: str, item_id: str) -> str:
    m = re.search(rf"(?ms)(^  - id: {re.escape(item_id)}\n.*?)(?=^  - id: |\Z)", text)
    if not m: raise AssertionError(f"missing registry entry {item_id}")
    return m.group(1)

def main() -> int:
    failures: list[str] = []
    s = write_status()
    print("JWT secret rotation evidence check")
    print(f"- INFO status: {s.status}")
    for p in CRITICAL:
        ast.parse(read(p)); print(f"- PASS syntax {p}")
    if os.getenv("JWT_EVIDENCE_ACCEPT") == "1":
        if s.status != ACCEPTED_STATUS: failures.extend(s.blockers)
        else:
            text = (ROOT / "docs/release/evidence_status_registry.yml").read_text(encoding="utf-8")
            for item in ["JWT-001", "JWT-001R"]:
                e = entry(text, item)
                for req in ["proof_status: runtime-passing", "closure_blocker: none", "release_ready: true", "blocks_beta: false"]:
                    if req not in e: failures.append(f"{item} missing {req}")
    else:
        print("- INFO acceptance not requested; tooling check only")
    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        r = subprocess.run([sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_jwt_secret_rotation_evidence.py", "-q", "--no-cov", "--tb=short"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)
        print(r.stdout)
        if r.returncode != 0: failures.append("JWT secret rotation unit tests failed")
    ruff = subprocess.run([sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if ruff.returncode == 0: print("- PASS focused Ruff JWT secret rotation check")
    else: failures.append("focused Ruff failed"); print(ruff.stdout)
    if failures:
        print("Failures:")
        for f in failures: print(f"- {f}")
        return 1
    print("- PASS JWT secret rotation evidence tooling check")
    return 0
if __name__ == "__main__": raise SystemExit(main())
