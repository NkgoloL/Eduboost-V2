from __future__ import annotations
import argparse, json, re
from scripts._subprocess import run
from pathlib import Path
from scripts.true_state_remediation.core import atomic_write_json, environment_manifest, git_state, root_from, sha256_file, utc_now

def migration_heads(root: Path) -> list[str]:
    proc=run(["alembic","heads"],cwd=root,text=True,capture_output=True,check=False, missing_executable="return")
    if proc.returncode==0:
        return [line.split()[0] for line in proc.stdout.splitlines() if line.strip()]
    revisions=[]; parents=[]
    for p in (root/"alembic/versions").glob("*.py"):
        t=p.read_text(errors="ignore")
        r=re.search(r"^revision\s*(?::[^=]+)?=\s*['\"]([^'\"]+)",t,re.M)
        d=re.search(r"^down_revision\s*(?::[^=]+)?=\s*['\"]([^'\"]+)",t,re.M)
        if r: revisions.append(r.group(1))
        if d: parents.append(d.group(1))
    return sorted(set(revisions)-set(parents))

def capture(root: Path, output: Path) -> dict:
    tracked=["README.md","docs/current_state.md","openapi.json","openapi.yaml","docs/openapi.json","docs/openapi.yaml","pnpm-lock.yaml","requirements/base.txt","requirements/dev.txt"]
    payload={
      "schema_version":"eduboost/true-state-remediation/baseline/v1",
      "captured_at":utc_now(),"git":git_state(root),"environment":environment_manifest(root),
      "digests":{p:sha256_file(root/p) for p in tracked if (root/p).is_file()},
      "migration_heads":migration_heads(root),
    }
    atomic_write_json(output,payload); return payload

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--output")
    a=ap.parse_args(); root=root_from(Path(a.repo)); out=Path(a.output) if a.output else root/"docs/release-evidence/true-state-remediation/b01/baseline_manifest.json"
    print(json.dumps(capture(root,out),indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
