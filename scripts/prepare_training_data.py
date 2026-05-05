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
TEACHING_PLANS_ROOT = PROJECT_ROOT / "data" / "temp" / "CAPS teaching plans"
OUTPUT_PATH = PROJECT_ROOT / "data" / "caps" / "training_data.jsonl"

def extract_sections(text: str) -> dict[str, str]:
    """
    Improved heuristic to extract sections based on 'Section X' or 'X.Y' headings.
    Attempts to avoid Table of Contents by looking for headers at the start of a line.
    """
    sections = {}
    
    for i in range(1, 5):
        # Pattern: Look for "SECTION X" or "X SECTION X" at the start of a line
        # This usually distinguishes the actual section from the Table of Contents
        pattern = rf"(?:\n|^)\s*\d?\s*SECTION\s+{i}\b.*?\n(.*?)(?=\n\s*\d?\s*SECTION\s+{i+1}\b|\n\s*\d?\s*SECTION\s+\d+\b|$)"
        match = re.search(pattern, text, re.S | re.I)
        if match:
            content = match.group(1).strip()
            # If content is very short, it might still be a TOC or a sub-header, 
            # so we try a broader search but only if the first one failed or was too small.
            if len(content) > 100:
                sections[f"section_{i}"] = content

    # Fallback for specifically named sections if the numbered ones didn't yield much
    if "section_3" not in sections or len(sections["section_3"]) < 500:
        match = re.search(r"(Section 3[:\s]+Content Specific Clarification.*?)(?=Section 4|$)", text, re.S | re.I)
        if match:
            sections["section_3"] = match.group(1).strip()

    return sections

def generate_pairs(doc: dict, sections: dict) -> list[dict]:
    pairs = []
    subject = doc.get("subject", "General")
    phase = doc.get("phase", "Unknown Phase")
    lang = doc.get("language", "English")
    grade = doc.get("grade", "")

    if grade:
        context = f"Grade {grade} {subject} ({phase} phase)"
    else:
        context = f"{subject} ({phase} phase)"

    if "section_1" in sections:
        pairs.append({
            "instruction": f"Provide an introduction to the CAPS curriculum for {context}.",
            "output": sections["section_1"][:2500]
        })

    if "section_2" in sections:
        pairs.append({
            "instruction": f"What are the specific aims and skills for {context} according to the South African CAPS guidelines?",
            "output": sections["section_2"][:2500]
        })

    if "section_3" in sections:
        pairs.append({
            "instruction": f"Give the content specific clarification and term-by-term breakdown for {context}.",
            "output": sections["section_3"][:4000]
        })

    if "section_4" in sections:
        pairs.append({
            "instruction": f"Explain the CAPS assessment requirements for {context}.",
            "output": sections["section_4"][:3000]
        })
        
    # Generic question about the document
    pairs.append({
        "instruction": f"What is the purpose of the '{doc['title']}' document?",
        "output": f"This document provides the Curriculum and Assessment Policy Statement (CAPS) for {subject} in the {phase} phase, specifically for {lang} instruction."
    })

    return pairs

def process_teaching_plans() -> list[dict]:
    """
    Process markdown teaching plans into training pairs.
    """
    pairs = []
    if not TEACHING_PLANS_ROOT.exists():
        LOGGER.warning(f"Teaching plans directory not found: {TEACHING_PLANS_ROOT}")
        return pairs

    for md_file in TEACHING_PLANS_ROOT.rglob("*.md"):
        grade = md_file.parent.name.replace("grade ", "").capitalize()
        subject = md_file.stem.replace("_", " ").capitalize()
        content = md_file.read_text(encoding="utf-8")
        
        # 1. Full plan overview
        pairs.append({
            "instruction": f"Generate a CAPS-aligned teaching plan overview for Grade {grade} {subject}.",
            "output": content.strip()
        })
        
        # 2. Term-based breakdown
        terms = re.split(r"## Term \d+", content)
        term_headers = re.findall(r"## (Term \d+.*)", content)
        
        for i, term_content in enumerate(terms[1:]):
            if i < len(term_headers):
                term_name = term_headers[i]
                pairs.append({
                    "instruction": f"What is covered in {term_name} for Grade {grade} {subject} according to the teaching plan?",
                    "output": f"In {term_name} for Grade {grade} {subject}, the following topics are covered:\n{term_content.strip()}"
                })
                
                # 3. Week-based breakdown
                weeks = re.findall(r"- (Week \d+.*)", term_content)
                for week in weeks:
                    pairs.append({
                        "instruction": f"What is the focus for {week.split(':')[0]} in Grade {grade} {subject} during {term_name.split(':')[0]}?",
                        "output": f"According to the Grade {grade} {subject} teaching plan, the focus for {week}."
                    })

    return pairs

def main():
    all_pairs = []
    
    # 1. Process CAPS PDFs from manifest
    if MANIFEST_PATH.exists():
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
    else:
        LOGGER.warning(f"Manifest not found at {MANIFEST_PATH}")

    # 2. Process Teaching Plans
    LOGGER.info("Processing teaching plans...")
    plan_pairs = process_teaching_plans()
    all_pairs.extend(plan_pairs)

    # 3. Save combined dataset
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w") as f:
        for pair in all_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    LOGGER.info(f"Generated {len(all_pairs)} training pairs at {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
