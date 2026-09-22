#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

STATUSES={"not_started","blocked","in_progress","candidate_complete","evidence_recorded","independent_review","closed","waived"}
def root_from(arg): return Path(arg).resolve()
def paths(root):
    reg=root/'docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json'
    ev=root/'docs/roadmap/production_readiness/lev/evidence'
    return reg,ev
def load(root):
    regp,ev=paths(root); return regp,json.loads(regp.read_text()),ev
def find(d,tid):
    tid=tid.removeprefix('LEV-')
    for t in d['tasks']:
        if t['id']==tid:return t
    raise SystemExit(f'unknown task: {tid}')
def main():
    p=argparse.ArgumentParser();p.add_argument('--repo-root',default='.')
    sp=p.add_subparsers(dest='cmd',required=True)
    sp.add_parser('status')
    s=sp.add_parser('show');s.add_argument('task_id')
    l=sp.add_parser('list');l.add_argument('--status');l.add_argument('--workstream')
    u=sp.add_parser('set-status');u.add_argument('task_id');u.add_argument('status',choices=sorted(STATUSES));u.add_argument('--owner');u.add_argument('--reviewer');u.add_argument('--note');u.add_argument('--evidence-type',choices=['synthetic_fixture','empirical_field'])
    a=p.parse_args(); root=root_from(a.repo_root); regp,d,evdir=load(root)
    if a.cmd=='status':
        counts={s:0 for s in STATUSES}
        for t in d['tasks']:counts[t['status']]+=1
        print(json.dumps({'total':len(d['tasks']),'counts':counts},indent=2));return
    if a.cmd=='show': print(json.dumps(find(d,a.task_id),indent=2));return
    if a.cmd=='list':
        rows=[t for t in d['tasks'] if (not a.status or t['status']==a.status) and (not a.workstream or t['workstream_id']==a.workstream)]
        for t in rows:print(f"{t['canonical_id']}\t{t['status']}\t{t['phase']}\t{t['action']}")
        return
    t=find(d,a.task_id); evp=evdir/f"{t['canonical_id']}.json"; ev=json.loads(evp.read_text())
    # Closed status is guarded: evidence, approval, and evidence_type are mandatory.
    if a.status=='closed':
        if (not ev.get('evidence_files') or not ev.get('approvals')):
            raise SystemExit('refusing closed: evidence_files and approvals must be populated')
        if t.get('cannot_be_completed_by_code_alone') and ev.get('evidence_type')!='empirical_field':
            raise SystemExit('refusing closed: human/field-dependent task cannot be closed without empirical_field evidence')
    t['status']=a.status;ev['status']=a.status;ev['updated_at']=datetime.now(timezone.utc).isoformat()
    if a.evidence_type:ev['evidence_type']=a.evidence_type
    if a.owner:t['owner']=a.owner;ev['owner']=a.owner
    if a.reviewer:t['reviewer']=a.reviewer;ev['reviewer']=a.reviewer
    if a.note:t.setdefault('notes',[]).append(a.note);ev.setdefault('notes',[]).append(a.note)
    regp.write_text(json.dumps(d,indent=2)+'\n');evp.write_text(json.dumps(ev,indent=2)+'\n')
    print(f"updated {t['canonical_id']} -> {a.status}")
if __name__=='__main__':main()
