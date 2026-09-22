#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path
def main():
 p=argparse.ArgumentParser();p.add_argument('--repo-root',default='.');p.add_argument('--output');a=p.parse_args();r=Path(a.repo_root).resolve();d=json.loads((r/'docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json').read_text());
 by=defaultdict(Counter)
 for t in d['tasks']:by[t['workstream_id']][t['status']]+=1
 lines=['# LEV Status Report','',f"Total tasks: {len(d['tasks'])}",'','| Workstream | Not started | Blocked | In progress | Candidate | Evidence | Review | Closed | Waived |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
 for ws in sorted(by):
  c=by[ws];lines.append(f"| {ws} | {c['not_started']} | {c['blocked']} | {c['in_progress']} | {c['candidate_complete']} | {c['evidence_recorded']} | {c['independent_review']} | {c['closed']} | {c['waived']} |")
 text='\n'.join(lines)+'\n';out=Path(a.output) if a.output else r/'docs/roadmap/production_readiness/lev/status_report.md';out.write_text(text);print(out)
if __name__=='__main__':main()
