#!/usr/bin/env python3
"""Resolve official DBE CAPS download URLs into the source manifest."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MANIFEST_PATH = ROOT / "data" / "caps" / "source_documents" / "manifest.json"

PHASE_URLS = {
    "foundation": "https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements%28CAPS%29/CAPSFoundation/tabid/571/Default.aspx",
    "intermediate": "https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements(CAPS)/CAPSIntermediate.aspx",
    "senior": "https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements(CAPS)/CAPSSenior.aspx",
}

SOURCE_TARGETS = {
    "caps_foundation_coding_and_robotics_en": ("foundation", "Coding and Robotics", "English"),
    "caps_foundation_home_language_en": ("foundation", "Home Languages", "English"),
    "caps_foundation_sepedi_first_additional_language_en": ("foundation", "First Additional Language", "Sepedi"),
    "caps_foundation_mathematics_en": ("foundation", "Mathematics", "English"),
    "caps_foundation_mathematics_grade_r_en": ("foundation", "Mathematics Grade R", "English"),
    "caps_foundation_life_skills_en": ("foundation", "Life Skills", "English"),
    "caps_intermediate_coding_and_robotics_en": ("intermediate", "Coding and Robotics", "English"),
    "caps_intermediate_home_language_en": ("intermediate", "Home Languages", "English"),
    "caps_intermediate_sepedi_first_additional_language_en": ("intermediate", "First Additional Language", "Sepedi"),
    "caps_intermediate_phase_mathematics_grade4_6": ("intermediate", "Nonlanguages in English", "Mathematics"),
    "caps_intermediate_natural_sciences_and_technology_en": ("intermediate", "Nonlanguages in English", "Natural Sciences and Technology"),
    "caps_intermediate_social_sciences_en": ("intermediate", "Nonlanguages in English", "Social Sciences"),
    "caps_intermediate_life_skills_en": ("intermediate", "Nonlanguages in English", "Life Skills"),
    "caps_senior_coding_and_robotics_en": ("senior", "Coding and Robotics", "English"),
    "caps_senior_home_language_en": ("senior", "Home Languages", "English"),
    "caps_senior_sepedi_first_additional_language_en": ("senior", "First Additional Language", "Sepedi"),
    "caps_senior_mathematics_en": ("senior", "NON LANGUAGES IN ENGLISH", "Mathematics"),
    "caps_senior_natural_sciences_en": ("senior", "NON LANGUAGES IN ENGLISH", "Natural Science"),
    "caps_senior_social_sciences_en": ("senior", "NON LANGUAGES IN ENGLISH", "Social Science"),
    "caps_senior_technology_en": ("senior", "NON LANGUAGES IN ENGLISH", "Technology"),
    "caps_senior_economic_management_sciences_en": ("senior", "NON LANGUAGES IN ENGLISH", "Economics Management and Science"),
    "caps_senior_life_orientation_en": ("senior", "NON LANGUAGES IN ENGLISH", "Life Orientation"),
    "caps_senior_creative_arts_en": ("senior", "NON LANGUAGES IN ENGLISH", "Creative Arts"),
}


@dataclass
class Link:
    phase: str
    section: str
    label: str
    href: str


class CapsLinkParser(HTMLParser):
    def __init__(self, phase: str, base_url: str) -> None:
        super().__init__()
        self.phase = phase
        self.base_url = base_url
        self.current_section = ""
        self._in_h2 = False
        self._current_href: str | None = None
        self._current_text: list[str] = []
        self.links: list[Link] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "h2":
            self._in_h2 = True
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href:
                self._current_href = urljoin(self.base_url, href)
                self._current_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "h2":
            self._in_h2 = False
            self.current_section = " ".join(self._current_text).strip()
            self._current_text = []
        if tag.lower() == "a" and self._current_href:
            label = " ".join(self._current_text).strip()
            self.links.append(Link(self.phase, self.current_section, label, self._current_href))
            self._current_href = None
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._in_h2 or self._current_href:
            value = data.strip()
            if value:
                self._current_text.append(value)


def normalize(value: str) -> str:
    return " ".join(value.lower().replace("&", "and").split())


def load_links() -> list[Link]:
    links: list[Link] = []
    for phase, url in PHASE_URLS.items():
        with urlopen(url, timeout=30) as response:
            html = response.read().decode("utf-8", errors="replace")
        parser = CapsLinkParser(phase, url)
        parser.feed(html)
        # Convert DBE table pattern: content anchor followed by Download anchor.
        pending_label: tuple[str, str] | None = None
        for link in parser.links:
            if normalize(link.label) == "download" and pending_label:
                section, label = pending_label
                links.append(Link(phase, section, label, link.href))
                pending_label = None
            elif link.section:
                pending_label = (link.section, link.label)
    return links


def resolve_targets(links: list[Link]) -> dict[str, str]:
    resolved: dict[str, str] = {}
    for document_id, (phase, section, label) in SOURCE_TARGETS.items():
        expected_section = normalize(section)
        expected_label = normalize(label)
        candidates = [
            link for link in links
            if link.phase == phase
            and normalize(link.section) == expected_section
            and normalize(link.label) == expected_label
        ]
        if candidates:
            resolved[document_id] = candidates[0].href
    return resolved


def update_manifest(resolved: dict[str, str], *, commit: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    changed: list[str] = []
    documents = {document["document_id"]: document for document in manifest["documents"]}

    if "caps_foundation_mathematics_grade_r_en" not in documents:
        grade_r_doc = {
            "document_id": "caps_foundation_mathematics_grade_r_en",
            "title": "CAPS Foundation Phase Mathematics Grade R",
            "publisher": "Department of Basic Education, South Africa",
            "curriculum": "CAPS",
            "phase": "foundation",
            "grades": [0],
            "subjects": ["Mathematics"],
            "languages": ["en"],
            "status": "planned",
            "language_role": "content_subject",
            "language_code": "eng",
            "canonical_source_url": None,
            "source_path": None,
            "object_store_uri": None,
            "source_hash": None,
            "source_sha256": None,
            "retrieved_at": None,
            "downloaded_at": None,
            "published_at": None,
            "reviewed_at": None,
            "reviewer_id": None,
            "evidence_notes": None,
            "notes": "Grade R Mathematics source is published separately from Grades 1-3 Mathematics on the DBE Foundation Phase CAPS page.",
        }
        manifest["documents"].append(grade_r_doc)
        documents[grade_r_doc["document_id"]] = grade_r_doc
        changed.append(grade_r_doc["document_id"])

    for document_id, url in resolved.items():
        document = documents.get(document_id)
        if not document:
            continue
        if document.get("canonical_source_url") != url:
            document["canonical_source_url"] = url
            changed.append(document_id)

    # Grade R Mathematics scope needs both Grade R and Grades 1-3 source records.
    scopes_path = ROOT / "data" / "content_factory" / "scopes.json"
    scopes = json.loads(scopes_path.read_text(encoding="utf-8"))
    for scope in scopes["scopes"]:
        if scope["scope_id"] == "grader_mathematics_en":
            expected = ["caps_foundation_mathematics_grade_r_en"]
            if scope.get("source_documents") != expected:
                scope["source_documents"] = expected
                changed.append(scope["scope_id"])
    if commit:
        manifest["documents"] = sorted(manifest["documents"], key=lambda item: item["document_id"])
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        scopes_path.write_text(json.dumps(scopes, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"resolved": resolved, "changed": sorted(set(changed))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="Update manifest/scopes with resolved URLs.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    links = load_links()
    resolved = resolve_targets(links)
    result = update_manifest(resolved, commit=args.commit)
    missing = sorted(set(SOURCE_TARGETS) - set(resolved))
    payload = {"resolved_count": len(resolved), "missing": missing, **result}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Resolved {len(resolved)}/{len(SOURCE_TARGETS)} DBE CAPS source URLs")
        if missing:
            print("Missing:")
            for document_id in missing:
                print(f"  - {document_id}")
        if args.commit:
            print(f"Updated: {', '.join(payload['changed']) if payload['changed'] else 'none'}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
