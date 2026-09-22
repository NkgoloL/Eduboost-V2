from __future__ import annotations
import json
from pathlib import Path

def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]

def test_lev_register_has_222_unique_tasks():
    root=repo_root();p=root/'docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json';d=json.loads(p.read_text())
    assert len(d['tasks'])==222
    assert len({t['id'] for t in d['tasks']})==222

def test_each_task_has_card_and_evidence_record():
    root=repo_root();d=json.loads((root/'docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json').read_text())
    for t in d['tasks']:
        assert (root/t['task_card']).is_file(), t['canonical_id']
        assert (root/t['task_evidence_record']).is_file(), t['canonical_id']

def test_closed_tasks_require_evidence_and_approval():
    root=repo_root();d=json.loads((root/'docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json').read_text())
    for t in d['tasks']:
        if t['status']=='closed':
            ev=json.loads((root/t['task_evidence_record']).read_text())
            assert ev['evidence_files']
            assert ev['approvals']

def test_closed_field_tasks_require_empirical_field_evidence():
    root=repo_root();d=json.loads((root/'docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json').read_text())
    for t in d['tasks']:
        if t['status']=='closed' and t.get('cannot_be_completed_by_code_alone'):
            ev=json.loads((root/t['task_evidence_record']).read_text())
            assert ev.get('evidence_type')=='empirical_field'

