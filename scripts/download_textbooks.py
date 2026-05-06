#!/usr/bin/env python3
import os
import requests
from pathlib import Path

# Base directories
BASE_DIR = Path("/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/data/caps/pdf")

# Siyavula Textbook patterns
SIYAVULA_URLS = [
    ("4", "natural_sciences", "https://www.siyavula.com/downloads/books/science/Gr4A_NaturalSciences_Learner_Eng.pdf"),
    ("4", "natural_sciences", "https://www.siyavula.com/downloads/books/science/Gr4B_NaturalSciences_Learner_Eng.pdf"),
    ("5", "natural_sciences", "https://www.siyavula.com/downloads/books/science/Gr5A_NaturalSciences_Learner_Eng.pdf"),
    ("5", "natural_sciences", "https://www.siyavula.com/downloads/books/science/Gr5B_NaturalSciences_Learner_Eng.pdf"),
    ("6", "natural_sciences", "https://www.siyavula.com/downloads/books/science/Gr6A_NaturalSciences_Learner_Eng.pdf"),
    ("6", "natural_sciences", "https://www.siyavula.com/downloads/books/science/Gr6B_NaturalSciences_Learner_Eng.pdf"),
    ("7", "maths", "https://www.siyavula.com/downloads/books/maths/Gr7A_Mathematics_Learner_Eng.pdf"),
    ("7", "maths", "https://www.siyavula.com/downloads/books/maths/Gr7B_Mathematics_Learner_Eng.pdf"),
    ("7", "natural_sciences", "https://www.siyavula.com/downloads/books/science/Gr7A_NaturalSciences_Learner_Eng.pdf"),
    ("7", "natural_sciences", "https://www.siyavula.com/downloads/books/science/Gr7B_NaturalSciences_Learner_Eng.pdf"),
]

def download_file(url, dest_path):
    if dest_path.exists():
        print(f"Skipping {dest_path.name}, already exists.")
        return True
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            dest_path.write_bytes(response.content)
            print(f"Downloaded: {dest_path.name}")
            return True
        else:
            print(f"Failed to download {url}: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def main():
    for grade, subject, url in SIYAVULA_URLS:
        grade_dir = BASE_DIR / f"grade{grade}"
        grade_dir.mkdir(parents=True, exist_ok=True)
        filename = os.path.basename(url)
        dest_path = grade_dir / filename
        download_file(url, dest_path)

if __name__ == "__main__":
    main()
