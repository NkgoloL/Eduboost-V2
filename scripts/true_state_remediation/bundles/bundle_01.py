from __future__ import annotations
import json, sys
from scripts._subprocess import run
from pathlib import Path
from scripts.true_state_remediation.core import (
 BundleError, atomic_write_json, environment_manifest, load_json, register_path, require_manual_evidence,
 run_command, CommandSpec, sha256_file, update_bundle_status, update_task_status, utc_now, verify_false_release_boundaries, verify_register,
)
TASKS=[f"TSR-0.{i}" for i in range(1,9)]+[f"TSR-1.{i}" for i in range(1,15)]
MANUAL=("TSR-0.7","TSR-1.11")

def prepare(*,root:Path,evidence_dir:Path,skip_heavy:bool):
    env=environment_manifest(root); atomic_write_json(evidence_dir/"environment_manifest.json",env)
    py=tuple(map(int,env["python"]["version"].split(".")[:2])); valid=py>=(3,12)
    return {"valid":valid,"python_supported":valid,"environment_manifest":str(evidence_dir/"environment_manifest.json")}

def apply(*,root:Path,evidence_dir:Path,skip_heavy:bool):
    capture=run_command(root,CommandSpec("capture_baseline",(sys.executable,"scripts/true_state_remediation/capture_baseline.py","--repo",str(root)),300),evidence_dir/"apply")
    if not capture["passed"]: return {"valid":False,"capture":capture}
    update_task_status(root,TASKS,"in_progress",[str((evidence_dir/"baseline_manifest.json").relative_to(root))])
    if skip_heavy: return {"valid":True,"structural_only":True}
    gates=run_command(root,CommandSpec("release_gates",(sys.executable,"scripts/true_state_remediation/run_release_gates.py","--repo",str(root)),10800),evidence_dir/"apply")
    return {"valid":gates["passed"],"gates":gates}

def verify(*,root:Path,evidence_dir:Path,skip_heavy:bool):
    checks={"register":verify_register(root),"boundaries":verify_false_release_boundaries(root)}
    baseline=evidence_dir/"baseline_manifest.json"; checks["baseline"]={"valid":baseline.exists()}
    mcp=(root/"tests/unit/test_etl_mcp_server_startup.py").read_text(errors="ignore")
    checks["mcp_isolation"]={"valid":"FASTMCP_BACKEND == \"test-stub\"" in mcp and "blocked_import" in mcp}
    if skip_heavy:
        valid=all(c.get("valid") for c in checks.values()); return {"valid":valid,"structural_only":True,"checks":checks}
    summary=load_json(evidence_dir/"commands/command_summary.json",{})
    checks["commands"]={"valid":summary.get("all_required_green") is True,"summary":summary}
    checks["manual"]=require_manual_evidence(root,"B01",MANUAL)
    valid=all(c.get("valid") for c in checks.values())
    if valid:
        update_task_status(root,TASKS,"verified",[str(evidence_dir.relative_to(root))])
        update_bundle_status(root,"B01","verified",next_bundle_status="authorised")
    else:
        update_task_status(root,TASKS,"evidence_pending",[str(evidence_dir.relative_to(root))])
        update_bundle_status(root,"B01","in_progress")
    atomic_write_json(evidence_dir/"verification.json",{"valid":valid,"checks":checks,"verified_at":utc_now()})
    return {"valid":valid,"checks":checks}
