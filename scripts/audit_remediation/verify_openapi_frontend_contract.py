#!/usr/bin/env python3
"""Verify the regenerated OpenAPI document and frontend route contract.

This is a dependency-light verifier. It reads committed files and does not import
FastAPI. Regeneration/currentness is handled by
``finalize_openapi_frontend_contract.sh`` using the project Python environment.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class RouteRequirement:
    frontend_fragment: str
    openapi_path: str
    method: str
    reason: str


REQUIRED_CONTRACT_ROUTES: tuple[RouteRequirement, ...] = (
    RouteRequirement('/popia/exports', '/api/v2/popia/exports', 'post', 'POPIA export request'),
    RouteRequirement('/popia/erasure', '/api/v2/popia/erasure', 'post', 'POPIA erasure request'),
    RouteRequirement('/popia/erasure/${learnerId}/cancel', '/api/v2/popia/erasure/{learner_id}/cancel', 'post', 'POPIA erasure cancellation'),
    RouteRequirement('/popia/erasure/${learnerId}/status', '/api/v2/popia/erasure/{learner_id}/status', 'get', 'POPIA erasure status'),
    RouteRequirement('/popia/restriction', '/api/v2/popia/restriction', 'post', 'POPIA processing restriction'),
    RouteRequirement('/parents/${guardianId}/export', '/api/v2/parents/{guardian_id}/export', 'get', 'parent export bundle'),
    RouteRequirement('/parents/${guardianId}/dashboard', '/api/v2/parents/{guardian_id}/dashboard', 'get', 'parent trust dashboard'),
    RouteRequirement('/parents/dashboard', '/api/v2/parents/dashboard', 'get', 'parent dashboard'),
    RouteRequirement('/consent/grant', '/api/v2/consent/grant', 'post', 'consent grant'),
    RouteRequirement('/consent/revoke', '/api/v2/consent/revoke', 'post', 'consent revoke'),
    RouteRequirement('/consent/status/${learnerId}', '/api/v2/consent/status/{learner_id}', 'get', 'consent status'),
    RouteRequirement('/lessons/generate', '/api/v2/lessons/generate', 'post', 'lesson generation'),
    RouteRequirement('/lessons/${lessonId}/complete', '/api/v2/lessons/{lesson_id}/complete', 'post', 'lesson completion'),
    RouteRequirement('/lessons/sync', '/api/v2/lessons/sync', 'post', 'lesson sync'),
    RouteRequirement('/learners/${learnerId}', '/api/v2/learners/{learner_id}', 'get', 'learner profile'),
    RouteRequirement('/learners/${learnerId}/mastery', '/api/v2/learners/{learner_id}/mastery', 'get', 'learner mastery'),
    RouteRequirement('/gamification/profile/${learnerId}', '/api/v2/gamification/profile/{learner_id}', 'get', 'gamification profile'),
    RouteRequirement('/gamification/award-xp', '/api/v2/gamification/award-xp', 'post', 'gamification XP award'),
    RouteRequirement('/study-plans/generate/${learnerId}', '/api/v2/study-plans/generate/{learner_id}', 'post', 'study-plan generation'),
    RouteRequirement('/diagnostics/submit', '/api/v2/diagnostics/submit', 'post', 'diagnostic submission'),
)

FORBIDDEN_FRONTEND_FRAGMENTS: tuple[str, ...] = (
    '/popia/data-export',
    '/popia/deletion-request',
    '/popia/deletion-cancel',
    '/popia/deletion-status',
    '/popia/restriction-request',
)

FORBIDDEN_PARENT_SNIPPETS: tuple[str, ...] = (
    '/api/v2/popia/data-export/',
    '/api/v2/popia/deletion-request/',
    '/api/v2/popia/deletion-cancel/',
    '/api/v2/popia/deletion-status/',
    '/api/v2/popia/restriction-request/',
)

REQUIRED_FILES = (
    'docs/openapi.json',
    'app/frontend/src/lib/api/services.ts',
    'app/api_v2_routers/parents.py',
    'app/api_v2_routers/popia.py',
    'scripts/generate_openapi.py',
    'scripts/audit_remediation/regenerate_openapi_contract.sh',
)


def _read(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding='utf-8')


def _load_openapi(root: Path) -> dict[str, Any]:
    return json.loads(_read(root, 'docs/openapi.json'))


def _method_present(paths: dict[str, Any], path: str, method: str) -> bool:
    methods = paths.get(path)
    if not isinstance(methods, dict):
        return False
    return method.lower() in {str(key).lower() for key in methods.keys()}


def _alias_path(path: str) -> str:
    if path.startswith('/api/v2/'):
        return '/v2/' + path[len('/api/v2/'):]
    return path


def _frontend_fragment_present(services_text: str, fragment: str) -> bool:
    # Support quoted literals and template literals. The fragment is checked as a
    # stable route substring, not as a full TypeScript parse tree.
    if fragment in services_text:
        return True
    escaped = re.escape(fragment).replace(re.escape('${'), r'\$\{')
    return re.search(escaped, services_text) is not None


def verify(root: Path = ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    for rel_path in REQUIRED_FILES:
        path = root / rel_path
        if path.exists():
            checked.append(rel_path)
        else:
            errors.append(f'missing required file: {rel_path}')

    try:
        openapi = _load_openapi(root)
    except FileNotFoundError:
        openapi = {'paths': {}}
    except json.JSONDecodeError as exc:
        errors.append(f'docs/openapi.json is invalid JSON: {exc}')
        openapi = {'paths': {}}

    paths = openapi.get('paths') if isinstance(openapi, dict) else {}
    if not isinstance(paths, dict):
        errors.append('docs/openapi.json must contain object-valued paths')
        paths = {}

    services = _read(root, 'app/frontend/src/lib/api/services.ts') if (root / 'app/frontend/src/lib/api/services.ts').exists() else ''
    parents = _read(root, 'app/api_v2_routers/parents.py') if (root / 'app/api_v2_routers/parents.py').exists() else ''
    popia = _read(root, 'app/api_v2_routers/popia.py') if (root / 'app/api_v2_routers/popia.py').exists() else ''

    for route in REQUIRED_CONTRACT_ROUTES:
        if not _method_present(paths, route.openapi_path, route.method):
            errors.append(f'OpenAPI missing {route.method.upper()} {route.openapi_path} ({route.reason})')
        alias = _alias_path(route.openapi_path)
        if alias != route.openapi_path and not _method_present(paths, alias, route.method):
            errors.append(f'OpenAPI missing {route.method.upper()} {alias} alias ({route.reason})')
        if not _frontend_fragment_present(services, route.frontend_fragment):
            errors.append(f'frontend services.ts missing route fragment {route.frontend_fragment} ({route.reason})')

    for forbidden in FORBIDDEN_FRONTEND_FRAGMENTS:
        if forbidden in services:
            errors.append(f'frontend services.ts still references retired route fragment {forbidden}')

    for forbidden in FORBIDDEN_PARENT_SNIPPETS:
        if forbidden in parents:
            errors.append(f'parent router still emits retired route fragment {forbidden}')

    if '/api/v2/popia/exports?learner_id=' not in parents:
        errors.append('parent router must emit canonical /api/v2/popia/exports?learner_id= export URLs')

    if '@router.get("/erasure/{learner_id}/status")' not in popia and "@router.get('/erasure/{learner_id}/status')" not in popia:
        errors.append('POPIA router must expose GET /erasure/{learner_id}/status')

    if errors:
        warnings.append('Regenerate OpenAPI with PYTHON_BIN=.venv/bin/python bash scripts/audit_remediation/finalize_openapi_frontend_contract.sh --regenerate')

    return {
        'valid': not errors,
        'errors': errors,
        'warnings': warnings,
        'checked': checked,
        'required_contract_routes': [
            {
                'frontend_fragment': route.frontend_fragment,
                'openapi_path': route.openapi_path,
                'method': route.method.upper(),
                'reason': route.reason,
            }
            for route in REQUIRED_CONTRACT_ROUTES
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()

    result = verify(args.root.resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print('OPENAPI FRONTEND CONTRACT PASSED' if result['valid'] else 'OPENAPI FRONTEND CONTRACT FAILED')
        for error in result['errors']:
            print(f'- {error}')
        for warning in result['warnings']:
            print(f'warning: {warning}')
    return 0 if result['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
