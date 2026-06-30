from __future__ import annotations

import asyncio
import json
from pathlib import Path
import uuid

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.content_factory import (
    ContentScope,
    ContentScopeStatus,
    ContentCoverageTarget,
    ContentGenerationArtifact,
    ContentArtifactSource,
    ContentLayer,
    ContentArtifactType,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCOPES_JSON = PROJECT_ROOT / "data" / "content_factory" / "scopes.json"
TARGETS_JSON = PROJECT_ROOT / "data" / "content_factory" / "coverage_targets.json"


async def ensure_scope(session, scope: dict) -> None:
    existing = await session.get(ContentScope, scope["scope_id"])
    if existing:
        return
    session.add(
        ContentScope(
            scope_id=scope["scope_id"],
            grade=int(scope["grade"]),
            subject_code=str(scope["subject_code"]),
            subject_slug=str(scope.get("subject", scope["subject_code"]).lower()),
            subject_display_name=str(scope.get("subject", scope["subject_code"])) ,
            language=str(scope["language"]),
            curriculum=str(scope.get("curriculum", "CAPS")),
            status=ContentScopeStatus.ACTIVE,
            source_policy={},
            targets={},
        )
    )
    await session.flush()


async def ensure_coverage_targets(session, targets: list[dict]) -> None:
    for entry in targets:
        scope_id = entry["scope_id"]
        caps_ref = entry["caps_ref"]
        for key, count in (entry.get("targets") or {}).items():
            layer_name, _, suffix = key.partition(".")
            if suffix != "approved":
                continue
            # Skip if this coverage target already exists
            existing = await session.execute(
                select(ContentCoverageTarget).where(
                    ContentCoverageTarget.scope_id == scope_id,
                    ContentCoverageTarget.caps_ref == caps_ref,
                    ContentCoverageTarget.content_layer == ContentLayer(layer_name),
                )
            )
            if existing.scalar_one_or_none() is not None:
                continue
            session.add(
                ContentCoverageTarget(
                    scope_id=scope_id,
                    caps_ref=caps_ref,
                    content_layer=ContentLayer(layer_name),
                    target_count=int(count),
                    minimum_approved_sources=1,
                )
            )
    await session.flush()


async def ensure_source_context(session, scope_id: str, caps_ref: str) -> None:
    # If any source exists for this caps_ref, skip
    result = await session.execute(
        select(ContentArtifactSource).where(ContentArtifactSource.caps_ref == caps_ref)
    )
    if result.scalar_one_or_none() is not None:
        return
    # Create a minimal artifact and source row
    artifact_id = uuid.uuid4()
    session.add(
        ContentGenerationArtifact(
            artifact_id=artifact_id,
            run_id=None,
            task_id=None,
            scope_id=scope_id,
            content_layer=ContentLayer.LESSONS,
            artifact_type=ContentArtifactType.LESSON,
            caps_ref=caps_ref,
            grade=4,
            subject_code="M",
            language="en",
            status="generated",
            artifact_json={"seed": True},
            artifact_hash=f"seed:{scope_id}:{caps_ref}",
        )
    )
    await session.flush()
    session.add(
        ContentArtifactSource(
            artifact_id=artifact_id,
            source_document_id=f"doc:{caps_ref}",
            source_chunk_id="chunk:1",
            source_title=f"Seed Source for {caps_ref}",
            citation_text=f"Seeded citation for {caps_ref}",
            caps_ref=caps_ref,
            grade=4,
            subject_code="M",
            language="en",
            license_status="public_domain",
            source_quality_score=0.9,
            source_hash=f"sha:{caps_ref}",
            curriculum_mapping_id=None,
            source_metadata={
                "document_status": "approved",
                "chunk_text": f"Seeded text for {caps_ref}",
                "chunk_quality_score": 0.9,
                "license_status": "public_domain",
            },
        )
    )
    await session.flush()


async def main() -> None:
    scopes_doc = json.loads(SCOPES_JSON.read_text(encoding="utf-8"))
    targets_doc = json.loads(TARGETS_JSON.read_text(encoding="utf-8"))
    async with AsyncSessionLocal() as session:
        for scope in scopes_doc.get("scopes", []):
            await ensure_scope(session, scope)
        await ensure_coverage_targets(session, [
            {"scope_id": t.get("scope_id", scopes_doc["scopes"][0]["scope_id"]), "caps_ref": t["caps_ref"], "targets": t["targets"]}
            for t in targets_doc.get("targets", [])
        ])
        # Seed minimal context for each caps_ref target
        for t in targets_doc.get("targets", []):
            scope_id = t.get("scope_id", scopes_doc["scopes"][0]["scope_id"])
            await ensure_source_context(session, scope_id, t["caps_ref"])
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
