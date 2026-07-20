#!/usr/bin/env python3
"""Gate 2R.3 focused verifier: extraction, page/section provenance, and chunks."""
from __future__ import annotations

import hashlib
import json
from scripts._subprocess import run
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run(command: list[str]) -> dict[str, object]:
    proc = run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return {"command": command, "exit_code": proc.returncode, "output": proc.stdout[-6000:]}


def behavioral_checks() -> list[str]:
    errors: list[str] = []
    try:
        from app.services.curriculum.extraction import StructuredTextExtractor, validate_extraction_result, ExtractionRejectedError

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "caps.txt"
            source.write_text(
                "NUMBERS, OPERATIONS AND RELATIONSHIPS\n\nLearners count, order and compare whole numbers.\f"
                "FRACTIONS:\n\nLearners recognise common fractions and solve 2 + 3 = 5.\n\n"
                "A  B  C\n1  2  3\n4  5  6\n7  8  9",
                encoding="utf-8",
            )
            result = StructuredTextExtractor(max_chunk_chars=180).extract_text_fixture(source, language="en")
            validation = validate_extraction_result(result)
            if validation:
                errors.append("valid fixture extraction failed validation: " + "; ".join(validation))
            if [page.page_number for page in result.pages] != [1, 2]:
                errors.append("page numbering/provenance failed")
            if not result.sections or not result.chunks:
                errors.append("sections/chunks were not created")
            if not all(len(item.text_sha256) == 64 for item in [*result.pages, *result.chunks]):
                errors.append("page/chunk text SHA-256 missing or invalid")
            if not any("formula_or_arithmetic_expression_detected" in chunk.warnings for chunk in result.chunks):
                errors.append("formula warning not propagated to chunks")
            try:
                StructuredTextExtractor().extract_text_fixture(source, language="zu")
                errors.append("invalid language was not rejected")
            except ExtractionRejectedError:
                pass
    except Exception as exc:
        errors.append(f"behavioral checks crashed: {exc}")
    return errors


def verify(*, include_real_source: bool) -> dict[str, object]:
    errors: list[str] = []
    checks: list[dict[str, object]] = []

    required = [
        "app/services/curriculum/extraction.py",
        "scripts/curriculum/extract_phase02r_sources.py",
        "scripts/verify_phase02r_gate2r3.py",
        "tests/unit/phase02r/test_gate2r3_extraction.py",
        "docs/roadmap/execution/atlas/phase_02r_gate_2r3_implementation_note.md",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        errors.append(f"missing required files: {missing}")

    gate = run([
        sys.executable,
        "scripts/phase02r_gate_control.py",
        "--expected-approved-gate", "2R.2",
        "--expected-authorised-gate", "2R.3",
        "--require-approval-roles",
        "--require-evidence-index-sha",
        "--json",
    ])
    checks.append(gate)
    if gate["exit_code"] != 0:
        errors.append("gate control does not authorise 2R.3")

    compile_check = run([
        sys.executable,
        "-m", "compileall", "-q",
        "app/services/curriculum/extraction.py",
        "scripts/curriculum/extract_phase02r_sources.py",
        "scripts/verify_phase02r_gate2r3.py",
        "tests/unit/phase02r/test_gate2r3_extraction.py",
    ])
    checks.append(compile_check)
    if compile_check["exit_code"] != 0:
        errors.append("compileall failed")

    tests = run([sys.executable, "-m", "pytest", "-q", "tests/unit/phase02r/test_gate2r3_extraction.py", "--no-cov"])
    checks.append(tests)
    if tests["exit_code"] != 0:
        errors.append("Gate 2R.3 focused unit tests failed")

    source_pdf = ROOT / "data" / "caps" / "source_documents" / "raw" / "caps_intermediate_phase_mathematics_grade4_6.pdf"
    if source_pdf.is_file() or include_real_source:
        dry_run = run([sys.executable, "scripts/curriculum/extract_phase02r_sources.py", "--dry-run", "--max-pages", "3", "--json"])
        checks.append(dry_run)
        if dry_run["exit_code"] != 0:
            errors.append("Gate 2R.3 real-source extraction dry-run failed")
    else:
        checks.append({"command": ["real-source-dry-run"], "exit_code": 0, "output": "skipped: controlled source PDF not present in this checkout"})

    if include_real_source:
        real_run = run([sys.executable, "scripts/curriculum/extract_phase02r_sources.py", "--max-pages", "5", "--json"])
        checks.append(real_run)
        if real_run["exit_code"] != 0:
            errors.append("Gate 2R.3 real-source extraction failed")
        else:
            try:
                payload = json.loads(real_run["output"])
                if not payload.get("passed"):
                    errors.append("Gate 2R.3 real-source extraction payload did not pass")
                if payload.get("controls", {}).get("corpus_membership_created") is not False:
                    errors.append("Gate 2R.3 extraction attempted to create corpus membership")
            except Exception as exc:
                errors.append(f"Gate 2R.3 real-source payload was not valid JSON: {exc}")

    errors.extend(behavioral_checks())
    return {"valid": not errors, "errors": errors, "checks": checks}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-real-source", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(include_real_source=args.include_real_source)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["valid"]:
        print("PHASE 02R GATE 2R.3 VERIFICATION PASSED")
    else:
        print("PHASE 02R GATE 2R.3 VERIFICATION FAILED", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
