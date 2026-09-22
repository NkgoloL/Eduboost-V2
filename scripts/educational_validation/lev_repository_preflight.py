#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
REQUIRED=['app','docs','scripts','tests','pyproject.toml','docs/roadmap/production_readiness/production_readiness_register.json','app/services/runtime_kg/service.py','app/modules/progress/mastery_model.py']
def main():
 p=argparse.ArgumentParser();p.add_argument('--repo-root',default='.');p.add_argument('--json',action='store_true');a=p.parse_args();r=Path(a.repo_root).resolve();missing=[x for x in REQUIRED if not (r/x).exists()]
 out={'valid':not missing,'repo_root':str(r),'missing':missing,'required':REQUIRED};print(json.dumps(out,indent=2) if a.json else out);raise SystemExit(0 if not missing else 1)
if __name__=='__main__':main()
