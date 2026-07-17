from __future__ import annotations
import json
import os
import shutil
import subprocess
from pathlib import Path
from scripts.knowledge_graph.audit_kg000_formal_kg_roadmap_approval import audit
from scripts.roadmap_reconciliation.verify_kg000_formal_kg_roadmap_approval import evaluate

def copy_payload(tmp_path: Path) -> Path:
    root = tmp_path / "repo"; root.mkdir(); payload = Path(__file__).resolve().parents[3]  # noqa: E702
    for rel in ["README.md","docs/README.md","docs/architecture/README.md","docs/adr/README.md","docs/roadmap/README.md","docs/roadmap/reconciliation/final_roadmap_reconciliation_closure_record.json"]:
        src = payload / rel
        if src.exists(): (root / rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, root / rel)  # noqa: E701, E702
    closure = root / "docs/roadmap/reconciliation/final_roadmap_reconciliation_closure_record.json"
    if not closure.exists():
        closure.parent.mkdir(parents=True, exist_ok=True)
        closure.write_text(json.dumps({"final_roadmap_reconciliation_closure_recorded": True,"all_reconciled_rr_items_addressed_through_rr018": True}), encoding="utf-8")
    for rel in ["docs/adr/ADR-036-knowledge-graph-learning-state-core.md","docs/architecture/knowledge_graph_learning_state_architecture.md","docs/architecture/knowledge_graph_data_model.md","docs/architecture/knowledge_graph_transition_plan.md","docs/product/knowledge_graph_learning_model_brief.md","docs/caps/knowledge_graph_mapping_contract.md","docs/ai/knowledge_graph_grounding_contract.md","docs/security/knowledge_graph_privacy_and_popia_contract.md","docs/testing/knowledge_graph_verification_plan.md","docs/roadmap/knowledge_graph_pivot_roadmap.md","docs/roadmap/risk_register_knowledge_graph_pivot.md","docs/roadmap/knowledge_graph/kg_implementation_roadmap.md","docs/roadmap/knowledge_graph/kg_roadmap_register.json","docs/roadmap/knowledge_graph/kg_formalization_package_manifest.json","docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval.md","docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval_record.json"]:
        src = payload / rel; assert src.exists(), rel; (root / rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, root / rel)  # noqa: E702
    for rel, text in {"README.md":"\nKnowledge Graph Roadmap ADR-036 kg_implementation_roadmap.md\n","docs/README.md":"\nKnowledge graph learning-state roadmap knowledge_graph_learning_state_architecture.md kg_implementation_roadmap.md\n","docs/architecture/README.md":"\nKnowledge Graph Learning-State Architecture knowledge_graph_data_model.md\n","docs/adr/README.md":"\nADR-036 Knowledge Graph Learning-State Core\n","docs/roadmap/README.md":"\nKG-0 kg_implementation_roadmap.md\n"}.items():
        path = root / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_text((path.read_text(encoding="utf-8") if path.exists() else "") + text, encoding="utf-8")  # noqa: E702
    record_path = root / "docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["formal_kg_roadmap_approval_recorded"] = False
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return root

def test_authority_audit_passes(tmp_path: Path):
    root = copy_payload(tmp_path); result = audit(root); assert result["authority_valid"], result; assert result["kg_ids"] == [f"KG-{i}" for i in range(9)]  # noqa: E702

def test_verifier_authority_only_before_capture(tmp_path: Path):
    root = copy_payload(tmp_path); result = evaluate(root); assert result["authority_valid"], result; assert not result["valid"]; assert not result["formal_kg_roadmap_approval_recorded"]  # noqa: E702

def test_capture_makes_record_valid(tmp_path: Path):
    root = copy_payload(tmp_path); subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL); subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True); subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True); subprocess.run(["git", "add", "."], cwd=root, check=True); subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL)  # noqa: E702
    payload = Path(__file__).resolve().parents[3]
    script = payload / "scripts/roadmap_reconciliation/capture_kg000_formal_kg_roadmap_approval_evidence.py"
    env = os.environ.copy(); env["PYTHONPATH"] = str(root) + os.pathsep + str(payload)  # noqa: E702
    subprocess.run(["python3", str(script), "--claim-kg000-formal-kg-roadmap-approval", "--kg-owner", "Nkgolo Lebelo", "--target-branch", "master", "--require-valid", "--json"], cwd=root, check=True, env=env)
    result = evaluate(root); assert result["valid"], result; assert result["runtime_kg_implementation_claimed"] is False  # noqa: E702

def test_boundary_flags_are_false_in_register(tmp_path: Path):
    root = copy_payload(tmp_path); register = json.loads((root / "docs/roadmap/knowledge_graph/kg_roadmap_register.json").read_text()); assert all(value is False for value in register["boundary"].values())  # noqa: E702

def test_kg0_does_not_authorise_runtime_kg(tmp_path: Path):
    root = copy_payload(tmp_path); record = json.loads((root / "docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval_record.json").read_text()); assert record["runtime_kg_implementation_claimed"] is False; assert record["runtime_kg_authority_switch_authorised"] is False; assert record["database_schema_migration_authorised"] is False  # noqa: E702
