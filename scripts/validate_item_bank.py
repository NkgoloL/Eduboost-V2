#!/usr/bin/env python3
"""
scripts/validate_item_bank.py
─────────────────────────────────────────────────────────────────────────────
Phase 3: Item Bank Offline Validation Runner (P2-05, P3-04)

Reads the seed JSON, runs all validators across every item, prints a
pass/fail report with item IDs, and exits with code 1 if any item fails.

Integrates with CI via:
    make validate-items
    # or directly:
    python scripts/validate_item_bank.py --input data/caps/grade4_maths_item_bank.json

Exit codes:
    0 — All items pass
    1 — One or more items failed validation
    2 — Input file not found or unparseable

Usage:
    python scripts/validate_item_bank.py
    python scripts/validate_item_bank.py --caps-ref 4.M.1.1
    python scripts/validate_item_bank.py --status approved --fail-fast
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.modules.diagnostics.item_validator import ItemValidator
from app.services.content_scope_registry import ContentScopeRegistry

DEFAULT_INPUT  = REPO_ROOT / "data" / "caps" / "grade4_maths_item_bank.json"
DEFAULT_SCOPE_ID = "grade4_mathematics_en"
FALLBACK_TOPIC_MAP_PATH = REPO_ROOT / "data" / "caps" / "caps_topic_map_grade4_maths.json"
FALLBACK_TARGET = 40


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_topic_map(*, scope_id: str, registry: ContentScopeRegistry) -> dict:
    scope = registry.get_scope(scope_id)
    topic_map_path = REPO_ROOT / scope.topic_map_path if scope.topic_map_path else FALLBACK_TOPIC_MAP_PATH
    if not topic_map_path.exists():
        print(f"⚠️  Topic map not found at {topic_map_path}. CAPS ref validation skipped.")
        return {}
    with open(topic_map_path) as f:
        return json.load(f)


def load_seed(input_path: Path) -> dict:
    if not input_path.exists():
        print(f"❌  Item bank file not found: {input_path}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(input_path) as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        print(f"❌  Cannot parse item bank JSON: {exc}", file=sys.stderr)
        sys.exit(2)


def coverage_summary(items: list[dict], *, scope_id: str, registry: ContentScopeRegistry) -> dict[str, dict]:
    scope = registry.get_scope(scope_id)
    refs = scope.caps_refs or sorted({str(item.get("caps_ref")) for item in items if item.get("caps_ref")})
    summary: dict[str, dict] = {}
    for ref in refs:
        ref_items = [i for i in items if i.get("caps_ref") == ref]
        approved  = [i for i in ref_items if i.get("review_status") == "approved"]
        target = _target_for_ref(scope_id, ref, registry=registry)
        summary[ref] = {
            "total":    len(ref_items),
            "approved": len(approved),
            "target":   target,
            "met":      len(approved) >= target,
        }
    return summary


def _target_for_ref(scope_id: str, caps_ref: str, *, registry: ContentScopeRegistry) -> int:
    targets = registry.get_scope_targets(scope_id)
    for target in targets:
        if target.caps_ref == caps_ref:
            value = target.targets.get("diagnostic_items.approved")
            if value is not None:
                return int(value)
    return FALLBACK_TARGET


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate all items in the CAPS item bank seed file."
    )
    parser.add_argument("--input", "--path", dest="input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument(
        "--scope-id",
        default=DEFAULT_SCOPE_ID,
        help="Registry scope to use for topic-map and coverage-target lookup.",
    )
    parser.add_argument(
        "--caps-ref",
        help="Only validate items for a specific CAPS ref, e.g. 4.M.1.1",
    )
    parser.add_argument(
        "--status",
        help="Only validate items with a specific review_status, e.g. approved",
    )
    parser.add_argument(
        "--fail-fast", action="store_true",
        help="Stop at the first failing item",
    )
    parser.add_argument(
        "--show-passing", action="store_true",
        help="Print a line for each passing item (default: only failures)",
    )
    parser.add_argument(
        "--fail-on-any-error", action="store_true",
        help="CI alias: exit non-zero if any validated item fails",
    )
    parser.add_argument(
        "--all-statuses", action="store_true",
        help="Validate all review statuses instead of defaulting to approved in CI mode",
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "github-annotations"],
        default="text",
        help="Output format for CI annotations",
    )
    args = parser.parse_args()

    if args.fail_on_any_error and not args.status and not args.all_statuses:
        args.status = "approved"

    registry = ContentScopeRegistry()
    topic_map = load_topic_map(scope_id=args.scope_id, registry=registry)
    seed      = load_seed(args.input)
    items     = seed.get("items", [])

    # Apply filters
    if args.caps_ref:
        items = [i for i in items if i.get("caps_ref") == args.caps_ref]
    if args.status:
        items = [i for i in items if i.get("review_status") == args.status]

    if not items:
        print("ℹ️  No items matched the given filters.")
        sys.exit(0)

    validator = ItemValidator(topic_map=topic_map)

    # Counters
    total   = len(items)
    passed  = 0
    failed  = 0
    failure_log: list[dict] = []

    print(f"\n{'='*65}")
    print("  EduBoost SA — Item Bank Validation")
    print(f"  Source: {args.input}")
    print(f"  Items to validate: {total}")
    if args.caps_ref:
        print(f"  Filter: caps_ref={args.caps_ref}")
    if args.status:
        print(f"  Filter: review_status={args.status}")
    print(f"{'='*65}\n")

    for item in items:
        item_id  = item.get("item_id", "??")[:12]
        caps_ref = item.get("caps_ref", "?")
        stem_preview = (item.get("stem") or "")[:60]

        errors = validator.validate_all(item)

        if not errors:
            passed += 1
            if args.show_passing:
                print(f"  ✅  {item_id}  [{caps_ref}]  {stem_preview}…")
        else:
            failed += 1
            if args.output_format == "github-annotations":
                for err in errors:
                    print(
                        "::error file=data/caps/grade4_maths_item_bank.json,"
                        f"title=Item Bank Validation [{err.rule}]::"
                        f"Item {item.get('item_id')}: {err.detail}"
                    )
            else:
                print(f"  ❌  {item_id}  [{caps_ref}]  {stem_preview}…")
                for err in errors:
                    print(f"       └─ [{err.rule}] {err.detail}")
            failure_log.append({
                "item_id":  item.get("item_id"),
                "caps_ref": caps_ref,
                "errors":   [{"rule": e.rule, "detail": e.detail} for e in errors],
            })
            if args.fail_fast:
                print("\n  🛑  --fail-fast: stopping at first failure.\n")
                break

    # Coverage summary
    all_items = seed.get("items", [])
    cov = coverage_summary(all_items, scope_id=args.scope_id, registry=registry)
    print(f"\n{'─'*65}")
    print(f"  Coverage Summary ({args.scope_id} — approved items vs target)")
    print(f"{'─'*65}")
    for ref, data in cov.items():
        status = "✅" if data["met"] else "⚠️ "
        print(
            f"  {status}  {ref:10s}  approved={data['approved']:3d} / {data['target']}  "
            f"(total generated={data['total']})"
        )

    # Validation summary
    print(f"\n{'─'*65}")
    print("  Validation Summary")
    print(f"{'─'*65}")
    print(f"  Total validated:  {total}")
    print(f"  Passed:           {passed}")
    print(f"  Failed:           {failed}")

    if failed == 0:
        if args.output_format == "github-annotations":
            print("::notice::Item bank validation passed — 0 failures.")
        print(f"\n  ✅  All {total} items passed validation.\n")
        sys.exit(0)
    else:
        pct = failed / total * 100
        print(f"\n  ❌  {failed}/{total} items failed ({pct:.1f}%). Fix before seeding.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
