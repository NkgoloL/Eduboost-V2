#!/usr/bin/env python3
"""Verify repo-side evidence for AI / LLM Pipeline roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['docs/curriculum/caps_topic_map_production_contract.md', 'docs/ai/production_lesson_generation_validation_contract.md', 'docs/ai/production_ai_pii_safety_contract.md', 'docs/ai/production_llm_gateway_contract.md', 'scripts/check_ai_llm_safety_caps_production_readiness.py', 'scripts/popia_sweep.py', 'scripts/check_ai_safety_boundary_contract.py', 'scripts/check_ai_output_schema_contract.py', 'scripts/validate_ai_output_fixtures.py', 'docs/ai', 'docs/llm', '.github/workflows/cluster-f-ai-safety.yml']
EXTERNAL_GATES = ['GitHub branch-protection / required-check UI settings require repository-admin access.', 'Green GitHub Actions status must be verified on GitHub after push.', 'Human owner, legal/privacy, security, curriculum, and release approvals cannot be supplied by an agent.', 'GPU provisioning/model registry/fine-tuning completion require cloud/model-registry access and human AI-safety review.']
TRACKED_GAPS = []

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 06: AI / LLM Pipeline")
    print(f"Repo evidence checked: {len(REQUIRED_EVIDENCE)} item(s)")
    if missing:
        print("Missing repo evidence:")
        for item in missing:
            print(f"- {item}")
        return 1
    print("Repo-side evidence files are present.")
    if TRACKED_GAPS:
        print("Tracked repo gaps from roadmap scope:")
        for item in TRACKED_GAPS:
            print(f"- {item}")
    if EXTERNAL_GATES:
        print("External/human gates remain outside repository verification:")
        for item in EXTERNAL_GATES:
            print(f"- {item}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
