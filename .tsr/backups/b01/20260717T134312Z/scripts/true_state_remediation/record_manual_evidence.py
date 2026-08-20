from __future__ import annotations

import argparse
from pathlib import Path

from scripts.true_state_remediation.core import record_manual_evidence, root_from


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a reviewed manual/external evidence artifact")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--control", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--reviewer-role", required=True)
    parser.add_argument("--decision", choices=("approved", "accepted_with_expiry", "completed", "rejected"), required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument("--expiry")
    args = parser.parse_args()
    root = root_from(Path(args.repo))
    path = record_manual_evidence(
        root, args.bundle, args.control, reviewer=args.reviewer, reviewer_role=args.reviewer_role,
        decision=args.decision, artifact_path=args.artifact, notes=args.notes, expiry=args.expiry,
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
