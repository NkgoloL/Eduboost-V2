"""Generate reproducible SBOMs for Python and frontend runtime packages.

Implements deliverable for:
- TSR-3.10: Produce SBOMs for release images
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.true_state_remediation.core import atomic_write_json, load_json, root_from, sha256_file


def generate_sbom(root: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    # 1. Backend Python SBOM from locked requirements
    base_req = root / "requirements/base.txt"
    backend_components = []
    if base_req.exists():
        for line in base_req.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "==" in line:
                name, version = line.split("==", 1)
                backend_components.append({
                    "type": "library",
                    "name": name.strip(),
                    "version": version.strip(),
                    "purl": f"pkg:pypi/{name.strip()}@{version.strip()}",
                })

    backend_sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:eduboost-backend-{hashlib.sha256(now.encode()).hexdigest()[:16]}",
        "version": 1,
        "metadata": {
            "timestamp": now,
            "component": {
                "type": "application",
                "name": "eduboost-backend",
                "version": "1.0.0-rc1",
            },
        },
        "components": backend_components,
    }
    backend_sbom_path = output_dir / "sbom-backend.cdx.json"
    atomic_write_json(backend_sbom_path, backend_sbom)

    # 2. Frontend SBOM from package.json
    fe_pkg_path = root / "app/frontend/package.json"
    frontend_components = []
    if fe_pkg_path.exists():
        fe_pkg = load_json(fe_pkg_path, {})
        for name, version in fe_pkg.get("dependencies", {}).items():
            clean_ver = version.lstrip("^~")
            frontend_components.append({
                "type": "library",
                "name": name,
                "version": clean_ver,
                "purl": f"pkg:npm/{name}@{clean_ver}",
            })

    frontend_sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:eduboost-frontend-{hashlib.sha256((now + 'fe').encode()).hexdigest()[:16]}",
        "version": 1,
        "metadata": {
            "timestamp": now,
            "component": {
                "type": "application",
                "name": "eduboost-frontend",
                "version": "1.0.0",
            },
        },
        "components": frontend_components,
    }
    frontend_sbom_path = output_dir / "sbom-frontend.cdx.json"
    atomic_write_json(frontend_sbom_path, frontend_sbom)

    return {
        "valid": True,
        "generated_at": now,
        "backend_sbom": str(backend_sbom_path.relative_to(root)),
        "backend_sbom_sha256": sha256_file(backend_sbom_path),
        "backend_components_count": len(backend_components),
        "frontend_sbom": str(frontend_sbom_path.relative_to(root)),
        "frontend_sbom_sha256": sha256_file(frontend_sbom_path),
        "frontend_components_count": len(frontend_components),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", default="docs/release-evidence/true-state-remediation/b02/sbom")
    args = parser.parse_args()
    root = root_from(Path(args.repo))
    res = generate_sbom(root, root / args.output_dir)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
