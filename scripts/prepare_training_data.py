#!/usr/bin/env python3
"""
Prepare instruction-tuning dataset from scraped CAPS documents.
This script parses the extracted text and generates JSONL pairs for LLM fine-tuning.
"""
import json
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
LOGGER = logging.getLogger("prepare_training")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "data" / "caps" / "manifest.jsonl"
OUTPUT_PATH = PROJECT_ROOT / "data" / "caps" / "training_data.jsonl"

def extract_sections(text: str) -> dict[str, str]:
    """
    Very simple heuristic to extract sections based on 'Section X' or 'X.Y' headings.
    In a real scenario, this would be much more sophisticated.
    """
    sections = {}
    
    # Try to find Section 3 (Content Specific Clarification) as it's the most valuable
    # Pattern: Section 3 ... Section 4
    match = re.search(r"(Section 3 Content Specific Clarification.*?)(?=Section 4|$)", text, re.S | re.I)
    if match:
        sections["section_3"] = match.group(1).strip()
        
    # Section 1 Introduction
    match = re.search(r"(Section 1 Introduction.*?)(?=Section 2|$)", text, re.S | re.I)
    if match:
        sections["section_1"] = match.group(1).strip()

    # Section 2 Definition, Aims, Skills
    match = re.search(r"(Section 2[:\s]+Definition.*?)(?=Section 3|$)", text, re.S | re.I)
    if match:
        sections["section_2"] = match.group(1).strip()

    return sections

def generate_pairs(doc: dict, sections: dict) -> list[dict]:
    pairs = []
    subject = doc.get("subject", "General")
    phase = doc.get("phase", "Unknown Phase")
    lang = doc.get("language", "English")

    if "section_1" in sections:
        pairs.append({
            "instruction": f"Provide an introduction to the CAPS curriculum for {subject} in the {phase} phase.",
            "output": sections["section_1"][:2000] # Limit size for demonstration
        })

    if "section_2" in sections:
        pairs.append({
            "instruction": f"What are the specific aims and skills for {subject} according to the South African CAPS guidelines for {phase}?",
            "output": sections["section_2"][:2000]
        })

    if "section_3" in sections:
        pairs.append({
            "instruction": f"Give the content specific clarification and term-by-term breakdown for {subject} in the {phase} phase.",
            "output": sections["section_3"][:3000]
        })
        
    # Generic question about the document
    pairs.append({
        "instruction": f"What is the purpose of the {doc['title']} document?",
        "output": f"This document provides the Curriculum and Assessment Policy Statement (CAPS) for {subject} in the {phase} phase, specifically for {lang} speakers/instruction."
    })

    return pairs

def main():
    if not MANIFEST_PATH.exists():
        LOGGER.error(f"Manifest not found at {MANIFEST_PATH}")
        return

    all_pairs = []
    with MANIFEST_PATH.open("r") as f:
        for line in f:
            doc = json.loads(line)
            text_path = Path(doc["local_text"])
            if not text_path.exists():
                LOGGER.warning(f"Text file not found: {text_path}")
                continue
            
            LOGGER.info(f"Processing {doc['title']}...")
            text = text_path.read_text(encoding="utf-8")
            sections = extract_sections(text)
            pairs = generate_pairs(doc, sections)
            all_pairs.extend(pairs)

    with OUTPUT_PATH.open("w") as f:
        for pair in all_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    LOGGER.info(f"Generated {len(all_pairs)} training pairs at {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
