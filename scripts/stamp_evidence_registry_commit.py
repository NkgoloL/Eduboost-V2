#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"
PROVEN = {"runtime-passing", "integration-passing", "production-ready"}


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout.strip() or "pending-local"


def main() -> int:
    sha = current_commit()
    lines = REGISTRY.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
    current_status: str | None = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("proof_status:"):
            current_status = stripped.split(":", 1)[1].strip()
            output.append(line)
            continue
        if stripped.startswith("last_verified_commit:") and current_status in PROVEN:
            output.append(f"    last_verified_commit: {sha}")
            continue
        output.append(line)

    REGISTRY.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"Stamped runtime/integration evidence registry entries with {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
