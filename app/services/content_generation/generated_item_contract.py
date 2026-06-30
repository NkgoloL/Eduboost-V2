"""Contract and quality validation for generated scope diagnostic items."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

GENERIC_ITEM_STEMS = (
    re.compile(r"^what should you do first\?$", re.I),
    re.compile(r"^which answer shows the best idea for .+\?$", re.I),
)

GENERIC_OPTION_PATTERNS = (
    re.compile(r"the answer follows the .+ facts in the question", re.I),
    re.compile(r"the answer guesses without checking", re.I),
    re.compile(r"the answer ignores the topic words", re.I),
    re.compile(r"the answer changes the order before solving", re.I),
)


@dataclass(frozen=True)
class GeneratedItemQualityIssue:
    item_id: str
    caps_ref: str
    field: str
    reason: str


@dataclass
class GeneratedItemQualityResult:
    passed: bool
    item_count: int
    failed_item_count: int
    issues: list[GeneratedItemQualityIssue] = field(default_factory=list)


class GeneratedItemQualityValidator:
    """Reject placeholder diagnostic items before staging or import."""

    def validate_item(self, item: dict) -> list[GeneratedItemQualityIssue]:
        item_id = str(item.get("item_id") or "unknown")
        caps_ref = str(item.get("caps_ref") or "unknown")
        issues: list[GeneratedItemQualityIssue] = []

        def add(field: str, reason: str) -> None:
            issues.append(GeneratedItemQualityIssue(item_id=item_id, caps_ref=caps_ref, field=field, reason=reason))

        stem = str(item.get("stem") or "").strip()
        if not stem:
            add("stem", "missing or empty")
        elif any(pattern.match(stem) for pattern in GENERIC_ITEM_STEMS):
            add("stem", f"generic placeholder stem: {stem[:80]}")

        options = item.get("options") or []
        if len(options) < 4:
            add("options", "fewer than four MCQ options")
        texts = [str(row.get("text") or "") for row in options if isinstance(row, dict)]
        if texts and len(set(texts)) != len(texts):
            add("options", "duplicate option text within item")

        answer_key = str(item.get("answer_key") or "")
        labels = {str(row.get("label") or "") for row in options if isinstance(row, dict)}
        if answer_key and labels and answer_key not in labels:
            add("answer_key", f"answer_key {answer_key!r} not in option labels")

        if texts and all(
            any(pattern.search(text) for pattern in GENERIC_OPTION_PATTERNS) for text in texts[:1]
        ):
            add("options", "options use generic study-behaviour distractors")

        explanation = str(item.get("explanation") or "").strip()
        if not explanation:
            add("explanation", "missing or empty")

        band = str(item.get("difficulty_band") or "")
        if band and band not in {"easy", "moderate", "on_level", "challenging"}:
            add("difficulty_band", f"unsupported band {band!r}")

        if str(item.get("source") or "") == "scope_scaffold":
            add("source", "legacy scope_scaffold source — regenerate with scope_item_generator_v2")

        return issues

    def validate_file_payload(self, payload: dict) -> GeneratedItemQualityResult:
        issues: list[GeneratedItemQualityIssue] = []
        stems_by_ref: dict[str, set[str]] = {}
        for item in payload.get("items") or []:
            item_issues = self.validate_item(item)
            issues.extend(item_issues)
            caps_ref = str(item.get("caps_ref") or "unknown")
            stem = str(item.get("stem") or "")
            ref_stems = stems_by_ref.setdefault(caps_ref, set())
            if stem in ref_stems:
                issues.append(
                    GeneratedItemQualityIssue(
                        item_id=str(item.get("item_id") or "unknown"),
                        caps_ref=caps_ref,
                        field="stem",
                        reason="duplicate stem within the same caps_ref",
                    )
                )
            ref_stems.add(stem)

        failed = len({issue.item_id for issue in issues})
        return GeneratedItemQualityResult(
            passed=not issues,
            item_count=len(payload.get("items") or []),
            failed_item_count=failed,
            issues=issues,
        )
