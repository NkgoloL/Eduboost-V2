from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_module(rel_path: str, name: str):
    module_path = Path(__file__).resolve().parents[3] / rel_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_fixture(root: Path) -> None:
    paths = {}
    for openapi_path, method in [
        ('/api/v2/popia/exports', 'post'),
        ('/api/v2/popia/erasure', 'post'),
        ('/api/v2/popia/erasure/{learner_id}/cancel', 'post'),
        ('/api/v2/popia/erasure/{learner_id}/status', 'get'),
        ('/api/v2/popia/restriction', 'post'),
        ('/api/v2/parents/{guardian_id}/export', 'get'),
        ('/api/v2/parents/{guardian_id}/dashboard', 'get'),
        ('/api/v2/parents/dashboard', 'get'),
        ('/api/v2/consent/grant', 'post'),
        ('/api/v2/consent/revoke', 'post'),
        ('/api/v2/consent/status/{learner_id}', 'get'),
        ('/api/v2/lessons/generate', 'post'),
        ('/api/v2/lessons/{lesson_id}/complete', 'post'),
        ('/api/v2/lessons/sync', 'post'),
        ('/api/v2/learners/{learner_id}', 'get'),
        ('/api/v2/learners/{learner_id}/mastery', 'get'),
        ('/api/v2/gamification/profile/{learner_id}', 'get'),
        ('/api/v2/gamification/award-xp', 'post'),
        ('/api/v2/study-plans/generate/{learner_id}', 'post'),
        ('/api/v2/diagnostics/submit', 'post'),
    ]:
        paths[openapi_path] = {method: {}}
        paths['/v2/' + openapi_path.removeprefix('/api/v2/')] = {method: {}}
    (root / 'docs').mkdir(parents=True)
    (root / 'docs/openapi.json').write_text(json.dumps({'paths': paths}), encoding='utf-8')
    (root / 'scripts/audit_remediation').mkdir(parents=True)
    (root / 'scripts/generate_openapi.py').parent.mkdir(parents=True, exist_ok=True)
    (root / 'scripts/generate_openapi.py').write_text('# stub\n', encoding='utf-8')
    (root / 'scripts/audit_remediation/regenerate_openapi_contract.sh').write_text('#!/usr/bin/env bash\n', encoding='utf-8')
    (root / 'app/frontend/src/lib/api').mkdir(parents=True)
    (root / 'app/frontend/src/lib/api/services.ts').write_text('''
fetchApi<DataExportBundle>("/popia/exports")
fetchApi<DataRightsStatus>("/popia/erasure")
fetchApi<DataRightsStatus>(`/popia/erasure/${learnerId}/cancel`)
fetchApi<DataRightsStatus>(`/popia/erasure/${learnerId}/status`)
fetchApi<DataRightsStatus>("/popia/restriction")
fetchApi<ParentExportBundle>(`/parents/${guardianId}/export`)
fetchApi<ParentTrustDashboardResponse>(`/parents/${guardianId}/dashboard`)
fetchApi<ParentDashboardResponse>("/parents/dashboard")
fetchApi<ConsentGrantResponse>("/consent/grant")
fetchApi<{ revoked: number }>("/consent/revoke")
fetchApi<ConsentStatusResponse>(`/consent/status/${learnerId}`)
fetchApi<JobAcceptedResponse>("/lessons/generate")
fetchApi<{ detail: string }>(`/lessons/${lessonId}/complete`)
fetchApi<{ processed: number }>("/lessons/sync")
fetchApi<ActiveLearner>(`/learners/${learnerId}`)
fetchApi<MasteryResponse>(`/learners/${learnerId}/mastery`)
fetchApi<GamificationProfile>(`/gamification/profile/${learnerId}`)
fetchApi<AwardXPResponse>("/gamification/award-xp")
fetchApi<JobAcceptedResponse>(`/study-plans/generate/${learnerId}`)
fetchApi<DiagnosticResult>("/diagnostics/submit")
''', encoding='utf-8')
    (root / 'app/api_v2_routers').mkdir(parents=True)
    (root / 'app/api_v2_routers/parents.py').write_text('export_url=f"/api/v2/popia/exports?learner_id={learner.id}"\n', encoding='utf-8')
    (root / 'app/api_v2_routers/popia.py').write_text('@router.get("/erasure/{learner_id}/status")\n', encoding='utf-8')


def test_openapi_frontend_contract_accepts_current_fixture(tmp_path: Path) -> None:
    module = load_module('scripts/audit_remediation/verify_openapi_frontend_contract.py', 'verify_openapi_frontend_contract')
    write_fixture(tmp_path)
    result = module.verify(tmp_path)
    assert result['valid'], result


def test_openapi_frontend_contract_rejects_retired_popia_alias(tmp_path: Path) -> None:
    module = load_module('scripts/audit_remediation/verify_openapi_frontend_contract.py', 'verify_openapi_frontend_contract_alias')
    write_fixture(tmp_path)
    services = tmp_path / 'app/frontend/src/lib/api/services.ts'
    services.write_text(services.read_text(encoding='utf-8') + '\nfetchApi("/popia/deletion-status/learner-1")\n', encoding='utf-8')
    result = module.verify(tmp_path)
    assert not result['valid']
    assert any('retired route fragment' in error for error in result['errors'])


def test_openapi_frontend_contract_rejects_missing_openapi_alias(tmp_path: Path) -> None:
    module = load_module('scripts/audit_remediation/verify_openapi_frontend_contract.py', 'verify_openapi_frontend_contract_missing')
    write_fixture(tmp_path)
    data = json.loads((tmp_path / 'docs/openapi.json').read_text(encoding='utf-8'))
    data['paths'].pop('/v2/popia/exports')
    (tmp_path / 'docs/openapi.json').write_text(json.dumps(data), encoding='utf-8')
    result = module.verify(tmp_path)
    assert not result['valid']
    assert any('/v2/popia/exports' in error for error in result['errors'])


def test_openapi_frontend_evidence_verifier_accepts_complete_bundle(tmp_path: Path) -> None:
    module = load_module('scripts/audit_remediation/verify_openapi_frontend_contract_evidence.py', 'verify_openapi_frontend_contract_evidence')
    evidence = tmp_path / 'evidence'
    raw = evidence / 'raw'
    raw.mkdir(parents=True)
    (evidence / 'evidence_index.md').write_text('Status: OpenAPI / frontend contract finalization passed — release readiness not claimed\n', encoding='utf-8')
    for name in ['openapi_route_contract.json', 'openapi_frontend_contract.json', 'popia_route_contract.json', 'frontend_tooling_evidence_check.json']:
        (raw / name).write_text(json.dumps({'valid': True, 'errors': []}), encoding='utf-8')
    (raw / 'openapi_finalize_check.txt').write_text('OPENAPI FRONTEND CONTRACT --check-only PASSED\n', encoding='utf-8')
    (raw / 'unit_tests.txt').write_text('4 passed\n', encoding='utf-8')
    (raw / 'openapi_sha256.txt').write_text('abc  docs/openapi.json\n', encoding='utf-8')
    import hashlib
    lines = []
    for path in sorted(raw.iterdir()):
        if path.name == 'SHA256SUMS.txt':
            continue
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (raw / 'SHA256SUMS.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    result = module.verify(evidence)
    assert result['valid'], result
