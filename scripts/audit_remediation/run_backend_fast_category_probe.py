#!/usr/bin/env python3
"""Run smaller probes that help split backend-fast failures before the full gate."""
from __future__ import annotations

import argparse
import json
import os
import shlex
from scripts._subprocess import run
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

DEFAULT_PROBES: tuple[tuple[str, str], ...] = (
    ("phase02r_terminal_gate_control", "{python} scripts/phase02r_gate_control.py --expected-approved-gate 2R.8 --expected-authorised-gate null --require-approval-roles --require-evidence-index-sha --json"),
    ("technical_audit_baseline", "{python} scripts/audit_remediation/verify_baseline_reset.py --json"),
    ("openapi_route_contract", "{python} scripts/audit_remediation/verify_openapi_route_contract.py --json"),
    ("popia_route_contract", "{python} scripts/audit_remediation/verify_popia_route_contract.py --json"),
    ("backend_fast_environment", "{python} scripts/audit_remediation/verify_backend_fast_environment.py --json"),
    ("migration_graph", "{python} scripts/verify_migration_graph.py"),
    ("schema_integrity", "{python} scripts/validate_schema_integrity.py"),
    ("runtime_entrypoints", "{python} scripts/check_runtime_entrypoints.py"),
    ("popia_wiring_units", "{python} -m pytest -q tests/unit/test_popia_*_authorization_wiring.py --no-cov"),
    ("audit_remediation_units", "{python} -m pytest -q tests/unit/audit_remediation --no-cov"),
)


def run_probe(name: str, command: str, *, root: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{name}.txt"
    started = time.time()
    completed = run(
        command,
        cwd=root,
        shell=True,  # nosec B602
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": os.environ.get("PYTHONPATH", ".")},
        check=False,
        timeout=int(os.environ.get("BACKEND_FAST_PROBE_TIMEOUT_SECONDS", "600")),
    )
    elapsed = round(time.time() - started, 3)
    output_file.write_text(f"$ {command}\n{completed.stdout}", encoding="utf-8", errors="replace")
    return {
        "name": name,
        "command": command,
        "command_tokens": shlex.split(command),
        "returncode": completed.returncode,
        "valid": completed.returncode == 0,
        "elapsed_seconds": elapsed,
        "output_file": str(output_file),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=Path("var/audit-remediation/backend-fast-category-probes"))
    parser.add_argument("--python-bin", default=os.environ.get("PYTHON_BIN", "python3"))
    parser.add_argument("--fail-on-failures", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    output_dir = (root / args.output_dir).resolve() if not args.output_dir.is_absolute() else args.output_dir
    results = [
        run_probe(name, template.format(python=args.python_bin), root=root, output_dir=output_dir)
        for name, template in DEFAULT_PROBES
    ]
    payload = {
        "valid": all(item["valid"] for item in results),
        "results": results,
        "failed_probe_names": [item["name"] for item in results if not item["valid"]],
        "output_dir": str(output_dir),
    }
    (output_dir / "probe_summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("BACKEND FAST CATEGORY PROBES PASSED" if payload["valid"] else "BACKEND FAST CATEGORY PROBES FAILED")
        for item in results:
            status = "PASS" if item["valid"] else "FAIL"
            print(f"{status} {item['name']} -> {item['output_file']}")
    if args.fail_on_failures and not payload["valid"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
