#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
LOGGER = logging.getLogger("organize_by_grade")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "data" / "caps" / "manifest.jsonl"
OUTPUT_BASE_DIR = PROJECT_ROOT / "data" / "caps" / "pdf"

PHASE_TO_GRADES = {
    "grades-r-3": ["r", "1", "2", "3"],
    "grades-4-6": ["4", "5", "6"],
    "grades-7-9": ["7"]
}

def get_target_grades(doc):
    title = doc.get("title", "").lower()
    phase = doc.get("phase", "")
    
    # Check for specific grade mentions first
    grade_match = re.search(r"grade\s*(r|[1-7])", title)
    if not grade_match:
        grade_match = re.search(r"gr\s*(r|[1-7])", title)
        
    if grade_match:
        target = grade_match.group(1)
        # If it's a specific grade, only return that one
        return [target]
    
    # If no specific grade, use the phase mapping
    return PHASE_TO_GRADES.get(phase, [])

def main():
    if not MANIFEST_PATH.exists():
        LOGGER.error(f"Manifest not found at {MANIFEST_PATH}")
        return

    # 1. Clean up existing grade directories
    # We'll handle 'r' and 1-7
    target_dirs = ["r"] + [str(i) for i in range(1, 8)]
    for g in target_dirs:
        grade_dir = OUTPUT_BASE_DIR / f"grade{g}"
        if grade_dir.exists():
            # Remove all symlinks to start fresh
            for f in grade_dir.iterdir():
                if f.is_symlink():
                    f.unlink()
        else:
            grade_dir.mkdir(parents=True, exist_ok=True)

    # 2. Process manifest
    with MANIFEST_PATH.open("r") as f:
        for line in f:
            if not line.strip(): continue
            doc = json.loads(line)
            pdf_path = Path(doc.get("local_pdf"))
            
            if not pdf_path.exists():
                LOGGER.warning(f"File not found: {pdf_path}")
                continue
                
            grades = get_target_grades(doc)
            for grade in grades:
                dest_dir = OUTPUT_BASE_DIR / f"grade{grade}"
                dest_path = dest_dir / pdf_path.name
                
                if not dest_path.exists():
                    # Create relative symlink
                    rel_src = os.path.relpath(pdf_path, dest_dir)
                    os.symlink(rel_src, dest_path)
                    LOGGER.info(f"Linked '{pdf_path.name}' to Grade {grade.upper()}")

    LOGGER.info("Organization complete.")

if __name__ == "__main__":
    main()
