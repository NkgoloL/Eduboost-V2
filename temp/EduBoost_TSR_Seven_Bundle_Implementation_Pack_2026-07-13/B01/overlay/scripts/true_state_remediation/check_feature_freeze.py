from __future__ import annotations
import argparse, json
from scripts._subprocess import run
from pathlib import Path
from scripts.true_state_remediation.core import load_json, register_path, root_from
ALLOWED_PREFIXES=("fix(","chore(remediation)","security(","privacy(","test(","refactor(","docs(current-state)","evidence(","control(")

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--title"); ap.add_argument("--json",action="store_true")
    a=ap.parse_args(); root=root_from(Path(a.repo)); reg=load_json(register_path(root),{})
    title=a.title or ""
    valid=reg.get("feature_freeze") is True and (not title or title.startswith(ALLOWED_PREFIXES) or "[approved-scope-exception]" in title)
    result={"valid":valid,"feature_freeze":reg.get("feature_freeze"),"title":title,"allowed_prefixes":ALLOWED_PREFIXES}
    print(json.dumps(result,indent=2,default=list) if a.json else result); return 0 if valid else 1
if __name__=="__main__": raise SystemExit(main())
