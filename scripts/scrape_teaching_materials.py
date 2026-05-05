#!/usr/bin/env python3
import os
import re
import json
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEACHING_PLANS_DIR = PROJECT_ROOT / "data" / "temp" / "CAPS teaching plans"
OUTPUT_BASE_DIR = PROJECT_ROOT / "data" / "caps" / "pdf"

START_URLS = {
    "foundation": "https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements/CAPSFoundation/tabid/571/Default.aspx",
    "intermediate": "https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements/CAPSIntermediate/tabid/572/Default.aspx",
    "senior": "https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements/CAPSSenior/tabid/573/Default.aspx",
    "atp": "https://www.education.gov.za/Resources/AnnualTeachingPlans.aspx"
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def fetch_html(url):
    print(f"Fetching: {url}")
    result = subprocess.run([
        "curl", "-s", "-L", "-H", f"User-Agent: {USER_AGENT}", url
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error fetching {url}: {result.stderr}")
        return ""
    return result.stdout

def get_pdf_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if ".pdf" in href.lower() or "linkclick.aspx" in href.lower():
            full_url = urljoin(base_url, href)
            links.append({"url": full_url, "text": text})
    return links

def download_pdf(url, dest_path):
    if dest_path.exists():
        return
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading: {url} -> {dest_path}")
    subprocess.run([
        "curl", "-s", "-L", "-H", f"User-Agent: {USER_AGENT}", "-o", str(dest_path), url
    ])

def main():
    # 1. Identify grades and subjects from the .md files
    grade_subjects = {}
    for grade_dir in TEACHING_PLANS_DIR.iterdir():
        if not grade_dir.is_dir():
            continue
        grade_match = re.search(r"grade\s*(\d+)", grade_dir.name.lower())
        if not grade_match:
            continue
        grade_num = grade_match.group(1)
        subjects = [f.stem for f in grade_dir.glob("*.md")]
        grade_subjects[grade_num] = subjects

    print(f"Found grades and subjects: {grade_subjects}")

    # 2. Scrape DBE pages for PDFs
    all_pdfs = []
    for name, url in START_URLS.items():
        html = fetch_html(url)
        links = get_pdf_links(html, url)
        all_pdfs.extend(links)
        print(f"Found {len(links)} PDFs on {name} page")

    # Subject mapping/synonyms
    SUBJECT_SYNONYMS = {
        "maths": ["mathematics", "wiskunde"],
        "english": ["english home language", "english first additional language"],
        "afrikaans": ["afrikaans huistaal", "afrikaans eerste addisionele taal"],
        "sepedi": ["sepedi home language", "sepedi first additional language"],
        "life_skills": ["life skills", "life orientation"],
        "natural_sciences": ["natural sciences", "natural sciences and technology", "natuurwetenskappe"],
        "social_sciences": ["social sciences", "sosiale wetenskappe"],
        "arts_culture": ["creative arts", "arts and culture", "kreatiewe kunste"]
    }

    # 3. Match PDFs to grades and subjects and download
    for grade_num, subjects in grade_subjects.items():
        grade_dir = OUTPUT_BASE_DIR / f"grade{grade_num}"
        grade_dir.mkdir(parents=True, exist_ok=True)
        
        g_num = int(grade_num)
        if 1 <= g_num <= 3:
            phase_hint = "foundation"
        elif 4 <= g_num <= 6:
            phase_hint = "intermediate"
        elif g_num == 7:
            phase_hint = "senior"
        else:
            phase_hint = "unknown"

        for subject in subjects:
            synonyms = SUBJECT_SYNONYMS.get(subject, [subject])
            sub_patterns = [s.lower() for s in synonyms]
            
            for pdf in all_pdfs:
                pdf_text = pdf["text"].lower()
                pdf_url = pdf["url"].lower()
                
                if subject == "maths" and grade_num == "1":
                     print(f"DEBUG: Checking PDF: '{pdf_text}' Patterns: {sub_patterns}")

                sub_match = any(pattern in pdf_text or pattern in pdf_url for pattern in sub_patterns)
                if not sub_match:
                    continue

                # Phase/Grade matching
                match = False
                if phase_hint in pdf_text or phase_hint in pdf_url:
                    match = True
                elif f"grade {grade_num}" in pdf_text or f"grade {grade_num}" in pdf_url:
                    match = True
                elif f"gr {grade_num}" in pdf_text or f"gr {grade_num}" in pdf_url:
                    match = True
                elif f"gr{grade_num}" in pdf_text or f"gr{grade_num}" in pdf_url:
                    match = True
                
                if match:
                    print(f"Matched: Grade {grade_num} {subject} -> {pdf['text']}")
                    filename = os.path.basename(urlparse(pdf["url"]).path)

                    if not filename.endswith(".pdf") or "linkclick" in filename.lower():
                        ticket_match = re.search(r"fileticket=([^&]+)", pdf["url"])
                        if ticket_match:
                            filename = f"{subject}_gr{grade_num}_{ticket_match.group(1)}.pdf"
                        else:
                            filename = f"{subject}_gr{grade_num}_{hash(pdf['url'])}.pdf"
                    
                    dest_path = grade_dir / filename
                    download_pdf(pdf["url"], dest_path)


if __name__ == "__main__":
    main()
