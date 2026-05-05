#!/usr/bin/env python3
import json
import os
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEACHING_PLANS_DIR = PROJECT_ROOT / "data" / "temp" / "CAPS teaching plans"
PDF_BASE_DIR = PROJECT_ROOT / "data" / "caps" / "pdf"

SUBJECT_SYNONYMS = {
    "maths": ["mathematics", "wiskunde", "maths"],
    "english": ["english", "home language", "language"],
    "afrikaans": ["afrikaans"],
    "sepedi": ["sepedi"],
    "life_skills": ["life skills", "life orientation", "lewensorientering"],
    "natural_sciences": ["natural science", "technology", "natuurwetenskappe", "tegnologie"],
    "social_sciences": ["social science", "sosiale wetenskappe"],
    "arts_culture": ["creative arts", "arts and culture", "skeppende kunste", "arts-subjects"]
}

def main():
    for grade_dir in TEACHING_PLANS_DIR.iterdir():
        if not grade_dir.is_dir(): continue
        grade_match = re.search(r"grade\s*(r|\d+)", grade_dir.name.lower())
        if not grade_match: continue
        grade_num = grade_match.group(1)
        
        grade_pdf_dir = PDF_BASE_DIR / f"grade{grade_num}"
        if not grade_pdf_dir.exists(): continue
        
        available_pdfs = list(grade_pdf_dir.glob("*.pdf"))
        
        for md_file in grade_dir.glob("*.md"):
            subject = md_file.stem
            synonyms = SUBJECT_SYNONYMS.get(subject, [subject])
            
            matched_pdfs = []
            for pdf in available_pdfs:
                pdf_name = pdf.name.lower()
                if any(syn.replace(" ", "-") in pdf_name or syn in pdf_name.replace("-", " ") for syn in synonyms):
                    matched_pdfs.append(pdf)
            
            if matched_pdfs:
                content = md_file.read_text()
                # Remove old section if exists (to allow re-population)
                content = re.sub(r"\n## Curriculum Resources.*", "", content, flags=re.DOTALL)
                
                resource_section = "\n## Curriculum Resources\n"
                # Filter out generic errata/guidelines unless no specific one found
                specific_pdfs = [p for p in matched_pdfs if any(s in p.name.lower() for s in synonyms)]
                
                # Sort to put most relevant first (e.g. ones containing "grade X")
                matched_pdfs.sort(key=lambda p: (f"grade-{grade_num}" in p.name.lower() or f"gr-{grade_num}" in p.name.lower()), reverse=True)

                for pdf in matched_pdfs[:5]: # Limit to top 5 most relevant
                    rel_path = os.path.relpath(pdf, md_file.parent)
                    resource_section += f"- [CAPS Document: {pdf.name}]({rel_path})\n"
                
                md_file.write_text(content.strip() + "\n" + resource_section)
                print(f"Updated {md_file.relative_to(PROJECT_ROOT)} with {len(matched_pdfs)} resources.")

if __name__ == "__main__":
    main()
