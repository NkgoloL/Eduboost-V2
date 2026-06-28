#!/usr/bin/env python3
"""Verify Phase 07 OpenAPI/frontend contract evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED_RAW_JSON = (
    'openapi_route_contract.json',
    'openapi_frontend_contract.json',
    'popia_route_contract.json',
    'frontend_tooling_evidence_check.json',
)
REQUIRED_RAW_TEXT = (
    'openapi_finalize_check.txt',
    'openapi_sha256.txt',
    'unit_tests.txt',
)


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return None, f'missing {path}'
    except json.JSONDecodeError as exc:
        return None, f'{path} is not valid JSON: {exc}'
    if not isinstance(data, dict):
        return None, f'{path} must contain a JSON object'
    return data, None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_sha_manifest(raw_dir: Path) -> list[str]:
    errors: list[str] = []
    manifest = raw_dir / 'SHA256SUMS.txt'
    if not manifest.exists():
        return ['missing raw/SHA256SUMS.txt']
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            errors.append(f'malformed SHA line: {line}')
            continue
        expected, rel = parts
        if rel == 'SHA256SUMS.txt':
            errors.append('SHA256SUMS.txt must not hash itself')
            continue
        target = raw_dir / rel
        if not target.exists():
            errors.append(f'SHA manifest references missing file: {rel}')
            continue
        actual = _sha256(target)
        if actual != expected:
            errors.append(f'SHA mismatch for {rel}: expected {expected}, actual {actual}')
    return errors


def verify(evidence_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    checked: list[str] = []
    raw_dir = evidence_dir / 'raw'
    if not raw_dir.exists():
        errors.append('missing raw evidence directory')
        raw_dir.mkdir(parents=True, exist_ok=True)

    index = evidence_dir / 'evidence_index.md'
    if index.exists():
        checked.append('evidence_index.md')
        text = index.read_text(encoding='utf-8')
        if 'Status: OpenAPI / frontend contract finalization passed' not in text:
            errors.append('evidence index must record passed OpenAPI / frontend contract status')
        if 'release readiness not claimed' not in text.lower():
            errors.append('evidence index must preserve release-readiness boundary')
    else:
        errors.append('missing evidence_index.md')

    for name in REQUIRED_RAW_JSON:
        path = raw_dir / name
        data, error = _load_json(path)
        if error:
            errors.append(error)
            continue
        checked.append(f'raw/{name}')
        if data and data.get('valid') is not True:
            errors.append(f'raw/{name} must report valid=true')
        if data and data.get('errors'):
            errors.append(f'raw/{name} must not contain errors: {data.get("errors")}')

    for name in REQUIRED_RAW_TEXT:
        path = raw_dir / name
        if not path.exists():
            errors.append(f'missing raw/{name}')
            continue
        checked.append(f'raw/{name}')
        text = path.read_text(encoding='utf-8', errors='replace')
        lowered = text.lower()
        if name == 'openapi_finalize_check.txt' and 'passed' not in lowered:
            errors.append('openapi_finalize_check.txt must record a passed finalize/check run')
        if name == 'unit_tests.txt' and 'passed' not in lowered:
            errors.append('unit_tests.txt must record passing focused tests')

    errors.extend(_verify_sha_manifest(raw_dir))
    if (raw_dir / 'SHA256SUMS.txt').exists():
        checked.append('raw/SHA256SUMS.txt')

    return {'valid': not errors, 'errors': errors, 'checked': checked}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    result = verify(args.evidence_dir.resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print('OPENAPI FRONTEND CONTRACT EVIDENCE PASSED' if result['valid'] else 'OPENAPI FRONTEND CONTRACT EVIDENCE FAILED')
        for error in result['errors']:
            print(f'- {error}')
    return 0 if result['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
