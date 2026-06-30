"""Diagnostic item generation and validation."""
from __future__ import annotations

from app.services.content_generation.prompt_payloads import GeneratedDiagnosticItem


class DiagnosticGenerator:
    def validate(self, item: GeneratedDiagnosticItem, *, caps_ref: str, existing_hashes: set[str] | None = None, artifact_hash: str | None = None) -> list[str]:
        errors: list[str] = []
        if not item.correct_answer:
            errors.append("diagnostic item requires an answer key.")
        if item.item_type == "single_choice":
            if len(item.options) < 2:
                errors.append("diagnostic item requires at least two options.")
            if item.options.count(item.correct_answer) != 1:
                errors.append("diagnostic item requires exactly one correct answer.")
        if not item.explanation:
            errors.append("diagnostic item requires an explanation.")
        if item.caps_ref != caps_ref:
            errors.append(f"diagnostic item caps_ref {item.caps_ref} does not match task caps_ref {caps_ref}.")
        if not item.source_chunk_ids:
            errors.append("diagnostic item requires source citations.")
        if artifact_hash and existing_hashes and artifact_hash in existing_hashes:
            errors.append("diagnostic item duplicates an existing artifact hash.")
        return errors
