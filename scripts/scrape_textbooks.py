#!/usr/bin/env python3
"""
EduBoost Textbook Downloader
Downloads official CAPS-aligned textbooks (Siyavula, DBE Workbooks)
and generates a metadata manifest.
"""

import os
import json
import requests
from pathlib import Path

# Base directories
BASE_DIR = Path("/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/data/caps")
PDF_DIR = BASE_DIR / "pdf"
MANIFEST_FILE = BASE_DIR / "books_manifest.jsonl"

# Known reliable sources (Siyavula Open Textbooks and discovered DBE links)
VERIFIED_RESOURCES = [
    # Grade 4 Siyavula (Natural Sciences)
    {"grade": "4", "subject": "natural_sciences", "title": "Gr4A Natural Sciences Learner", "isbn": None, "source": "Siyavula", "url": "https://www.siyavula.com/downloads/books/science/Gr4A_NaturalSciences_Learner_Eng.pdf"},
    {"grade": "4", "subject": "natural_sciences", "title": "Gr4B Natural Sciences Learner", "isbn": None, "source": "Siyavula", "url": "https://www.siyavula.com/downloads/books/science/Gr4B_NaturalSciences_Learner_Eng.pdf"},
    
    # Grade 5 Siyavula (Natural Sciences)
    {"grade": "5", "subject": "natural_sciences", "title": "Gr5A Natural Sciences Learner", "isbn": None, "source": "Siyavula", "url": "https://www.siyavula.com/downloads/books/science/Gr5A_NaturalSciences_Learner_Eng.pdf"},
    {"grade": "5", "subject": "natural_sciences", "title": "Gr5B Natural Sciences Learner", "isbn": None, "source": "Siyavula", "url": "https://www.siyavula.com/downloads/books/science/Gr5B_NaturalSciences_Learner_Eng.pdf"},
    
    # Grade 6 Siyavula (Natural Sciences)
    {"grade": "6", "subject": "natural_sciences", "title": "Gr6A Natural Sciences Learner", "isbn": None, "source": "Siyavula", "url": "https://www.siyavula.com/downloads/books/science/Gr6A_NaturalSciences_Learner_Eng.pdf"},
    {"grade": "6", "subject": "natural_sciences", "title": "Gr6B Natural Sciences Learner", "isbn": None, "source": "Siyavula", "url": "https://www.siyavula.com/downloads/books/science/Gr6B_NaturalSciences_Learner_Eng.pdf"},
    
    # Grade 7 Siyavula (Mathematics)
    {"grade": "7", "subject": "maths", "title": "Gr7A Mathematics Learner", "isbn": None, "source": "Siyavula", "url": "https://www.siyavula.com/downloads/books/maths/Gr7A_Mathematics_Learner_Eng.pdf"},
    {"grade": "7", "subject": "maths", "title": "Gr7B Mathematics Learner", "isbn": None, "source": "Siyavula", "url": "https://www.siyavula.com/downloads/books/maths/Gr7B_Mathematics_Learner_Eng.pdf"},
    
    # Grade 7 DBE Rainbow Workbook (Verified Link)
    {"grade": "7", "subject": "maths", "title": "Grade 7 Mathematics Book 2", "isbn": "978-1-4315-0220-2", "source": "DBE Rainbow Workbook", "url": "https://www.education.gov.za/LinkClick.aspx?fileticket=kXUFKKFhSGo%3D&mid=1561&portalid=0&tabid=571", "filename": "Grade7_Maths_Book2.pdf"},
]

def download_file(url, dest_path):
    """Downloads a file with basic error handling and progress indication."""
    if dest_path.exists():
        print(f"[-] Skipping {dest_path.name}, already exists.")
        return True
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        print(f"[*] Downloading {dest_path.name}...")
        response = requests.get(url, headers=headers, timeout=60, stream=True)
        if response.status_code == 200:
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[+] Successfully downloaded: {dest_path.name}")
            return True
        else:
            print(f"[!] Failed to download {url}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[!] Error downloading {url}: {e}")
        return False

def update_manifest(metadata):
    """Appends metadata to the JSONL manifest."""
    with open(MANIFEST_FILE, "a") as f:
        f.write(json.dumps(metadata) + "\n")

def main():
    print("=== EduBoost Textbook Curation Pipeline ===")
    
    # Ensure manifest exists or clear it to rebuild based on current seeds
    if MANIFEST_FILE.exists():
        MANIFEST_FILE.unlink()
        
    success_count = 0
    
    for resource in VERIFIED_RESOURCES:
        grade = resource["grade"]
        url = resource["url"]
        
        grade_dir = PDF_DIR / f"grade{grade}"
        grade_dir.mkdir(parents=True, exist_ok=True)
        
        # Use provided filename or extract from URL
        filename = resource.get("filename")
        if not filename:
            # Handle standard URLs
            filename = url.split("/")[-1].split("?")[0]
            
        dest_path = grade_dir / filename
        
        if download_file(url, dest_path):
            success_count += 1
            # Build manifest entry
            manifest_entry = {
                "grade": grade,
                "subject": resource["subject"],
                "title": resource["title"],
                "isbn": resource.get("isbn"),
                "source": resource["source"],
                "file_path": str(dest_path.relative_to(BASE_DIR.parent))
            }
            update_manifest(manifest_entry)
            
    print(f"\n=== Curation Complete. Processed {success_count}/{len(VERIFIED_RESOURCES)} textbooks. ===")

if __name__ == "__main__":
    main()
