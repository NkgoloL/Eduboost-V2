import argparse
import importlib
import json
import sys
import traceback
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.true_state_remediation.core import (
    BundleError,
    environment_manifest,
    evidence_root,
    root_from,
    verify_false_release_boundaries,
    verify_previous_bundle,
    write_bundle_state,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute a controlled EduBoost true-state remediation bundle")
    parser.add_argument("--bundle", required=True, choices=[f"B{i:02d}" for i in range(1, 8)])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--phase", choices=("prepare", "apply", "verify", "all"), default="all")
    parser.add_argument("--skip-heavy", action="store_true", help="Run structural smoke checks only; cannot close a bundle")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = root_from(Path(args.repo))
    bundle_id = args.bundle
    module_name = f"scripts.true_state_remediation.bundles.bundle_{bundle_id[1:].lower()}"
    evidence = evidence_root(root, bundle_id)
    evidence.mkdir(parents=True, exist_ok=True)
    result = {
        "bundle_id": bundle_id,
        "valid": False,
        "phase": args.phase,
        "skip_heavy": args.skip_heavy,
        "environment": environment_manifest(root),
    }
    try:

        previous = verify_previous_bundle(root, bundle_id)
        if not previous["valid"]:
            raise BundleError(f"Previous bundle is not verified: {previous}")
        boundaries = verify_false_release_boundaries(root) if bundle_id != "B07" else {"valid": True, "mode": "B07 decisions validated by final-program verifier"}
        if not boundaries["valid"]:
            raise BundleError(f"Release boundaries are not fail-closed: {boundaries['failures']}")
        module = importlib.import_module(module_name)
        phases = ("prepare", "apply", "verify") if args.phase == "all" else (args.phase,)
        phase_results = {}
        for phase in phases:
            handler = getattr(module, phase)
            phase_results[phase] = handler(root=root, evidence_dir=evidence, skip_heavy=args.skip_heavy)
            if not phase_results[phase].get("valid", False):
                raise BundleError(f"{bundle_id} {phase} failed: {phase_results[phase]}")
        final_verify = phase_results.get("verify")
        if final_verify is None and args.phase != "prepare":
            final_verify = module.verify(root=root, evidence_dir=evidence, skip_heavy=args.skip_heavy)
        if args.skip_heavy:
            result.update({"valid": False, "smoke_valid": all(v.get("valid") for v in phase_results.values()), "reason": "skip-heavy cannot close a bundle", "phases": phase_results})
        else:
            valid = bool(final_verify and final_verify.get("valid"))
            result.update({"valid": valid, "phases": phase_results, "environment": environment_manifest(root)})
        write_bundle_state(root, bundle_id, result)
    except Exception as exc:
        result.update({"valid": False, "error": str(exc), "traceback": traceback.format_exc()})
        write_bundle_state(root, bundle_id, result)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
