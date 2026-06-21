#!/usr/bin/env python3
"""Load Gate 2R.1 source authority and per-use rights records."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
import uuid
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.curriculum.validate_source_completeness_register import (  # noqa: E402
    DEFAULT_REGISTER,
    validate,
)

DEFAULT_SOURCE_MANIFEST = ROOT / "data" / "caps" / "source_documents" / "manifest.json"
TARGET_DOCUMENT_ID = "caps_intermediate_phase_mathematics_grade4_6"
LOADER_NAMESPACE = uuid.UUID("3f8a2067-aad1-5479-8ec6-eaf1f480b5a3")
CREATED_BY = "phase-02r-gate2r1-authority-loader"
USER_AGENT = "Eduboost-Phase02R-authority-loader/1.0"

RIGHTS_FIELDS = (
    "may_store_original",
    "may_extract",
    "may_embed",
    "may_use_for_retrieval",
    "may_include_in_model_prompt",
    "may_generate_derivatives",
    "may_translate",
    "may_publish_translation",
    "may_show_excerpt_to_educator",
    "may_show_excerpt_to_learner",
    "may_redistribute",
    "may_use_commercially",
    "may_use_for_model_training",
    "requires_attribution",
)


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_publication_date(value: str | None) -> date | None:
    if not value:
        return None
    if value.isdigit() and len(value) == 4:
        return date(int(value), 1, 1)
    return date.fromisoformat(value)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_value(value: Any) -> Any:
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, datetime):
        value = value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
        return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: stable_value(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [stable_value(item) for item in value]
    return value


def jsonb_value(value: Any) -> Any:
    if isinstance(value, str):
        return json.loads(value)
    return value


def field_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(stable_value(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def assert_field_match(label: str, actual: dict[str, Any], expected: dict[str, Any]) -> None:
    normalized_actual = stable_value(actual)
    normalized_expected = stable_value(expected)
    if normalized_actual != normalized_expected:
        raise RuntimeError(
            f"{label} content mismatch after idempotent load: "
            f"expected_hash={field_hash(expected)} actual_hash={field_hash(actual)}"
        )


def download_pdf(url: str, target: Path) -> int:
    target.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=90) as response:
        payload = response.read()
    if not payload.startswith(b"%PDF-"):
        preview = payload[:120].decode("utf-8", errors="replace").replace("\n", " ")
        raise RuntimeError(f"downloaded source is not a PDF: {preview!r}")
    tmp = target.with_suffix(target.suffix + ".part")
    tmp.write_bytes(payload)
    tmp.replace(target)
    return len(payload)


def source_manifest_document(manifest: dict[str, Any]) -> dict[str, Any]:
    for document in manifest.get("documents", []):
        if document.get("document_id") == TARGET_DOCUMENT_ID:
            return document
    raise RuntimeError(f"{TARGET_DOCUMENT_ID} is missing from {DEFAULT_SOURCE_MANIFEST}")


def ensure_verified_source_file(document: dict[str, Any], *, download_missing: bool) -> tuple[Path, int, str, bool]:
    source_path = document.get("source_path")
    if not source_path:
        raise RuntimeError(f"{TARGET_DOCUMENT_ID} has no source_path")

    target = ROOT / source_path
    downloaded = False
    if not target.is_file():
        if not download_missing:
            raise RuntimeError(f"{source_path} is missing; rerun with --download-missing to reacquire it")
        url = document.get("canonical_source_url") or document.get("object_store_uri")
        if not url:
            raise RuntimeError(f"{TARGET_DOCUMENT_ID} has no download URL")
        download_pdf(str(url), target)
        downloaded = True

    byte_count = target.stat().st_size
    checksum = sha256_file(target)
    expected = document.get("source_sha256") or document.get("source_hash")
    if checksum != expected:
        raise RuntimeError(f"{source_path} SHA-256 mismatch: expected {expected}, got {checksum}")
    return target, byte_count, checksum, downloaded


def load_register(path: Path) -> dict[str, Any]:
    document = read_json(path)
    errors = validate(document, require_frozen=True)
    if errors:
        raise RuntimeError("source-completeness register is not closure-ready: " + "; ".join(errors))
    return document


def build_records(
    register: dict[str, Any],
    source_document: dict[str, Any],
    *,
    source_path: Path,
    file_size_bytes: int,
    source_sha256: str,
    downloaded: bool,
) -> dict[str, Any]:
    located_items = [item for item in register["items"] if item.get("item_status") == "located"]
    if not located_items:
        raise RuntimeError("source-completeness register has no located authority items")

    source_ids = {item["source_id"] for item in located_items}
    source_version_ids = {item["source_version_id"] for item in located_items}
    if len(source_ids) != 1 or len(source_version_ids) != 1:
        raise RuntimeError("Gate 2R.1 loader expects one located source/version for the first closure slice")

    primary_item = located_items[0]
    evidence = primary_item["evidence"]
    rights = evidence["rights_determination"]
    scope = register["scope"]
    inventory_version_id = uuid.uuid5(
        LOADER_NAMESPACE,
        f"inventory:{register['inventory_code']}:{register['version_number']}:{register['manifest_sha256']}",
    )
    rights_decision_id = uuid.uuid5(
        LOADER_NAMESPACE,
        f"rights:{primary_item['source_version_id']}:{rights['decision_status']}:{register['manifest_sha256']}",
    )

    retrieval_metadata = {
        "source_manifest_document_id": TARGET_DOCUMENT_ID,
        "source_manifest_path": str(DEFAULT_SOURCE_MANIFEST.relative_to(ROOT)),
        "source_manifest_status": source_document.get("status"),
        "source_path": str(source_path.relative_to(ROOT)),
        "downloaded_during_load": downloaded,
        "canonical_source_url": source_document.get("canonical_source_url"),
        "object_store_uri": source_document.get("object_store_uri"),
        "register_manifest_sha256": register["manifest_sha256"],
    }
    source = {
        "source_id": uuid.UUID(primary_item["source_id"]),
        "publisher": evidence["source_publisher"],
        "authority_tier": primary_item["authority_tier"],
        "official_source_url": source_document.get("canonical_source_url") or evidence.get("source_uri"),
        "document_title": evidence["source_title"],
        "document_type": evidence["document_type"],
        "country": scope.get("country", "ZA"),
        "curriculum": scope["curriculum"],
        "phase": source_document.get("phase"),
        "grade": scope["grade"],
        "subject": scope["subject"],
        "language": primary_item["language"],
        "created_by": CREATED_BY,
    }
    source_version = {
        "source_version_id": uuid.UUID(primary_item["source_version_id"]),
        "source_id": uuid.UUID(primary_item["source_id"]),
        "version_label": evidence["source_reference"],
        "publication_date": parse_publication_date(evidence.get("publication_date")),
        "effective_from": parse_publication_date(evidence.get("publication_date")),
        "effective_to": None,
        "copyright_owner": evidence["source_publisher"],
        "original_sha256": source_sha256,
        "original_object_uri": source_document["object_store_uri"],
        "media_type": "application/pdf",
        "file_size_bytes": file_size_bytes,
        "retrieved_at": parse_timestamp(source_document["retrieved_at"]),
        "retrieval_metadata": retrieval_metadata,
        "created_by": CREATED_BY,
    }
    rights_decision = {
        "rights_decision_id": rights_decision_id,
        "source_version_id": uuid.UUID(primary_item["source_version_id"]),
        "decision_status": rights["decision_status"],
        **{field: bool(rights.get(field, False)) for field in RIGHTS_FIELDS},
        "conditions": dict(rights.get("conditions") or {}),
        "decision_basis": rights["decision_basis"],
        "evidence_uri": rights["evidence_uri"],
        "reviewed_by": primary_item["reviewed_by"],
        "reviewed_at": parse_timestamp(primary_item["reviewed_at"]),
        "expires_at": None,
        "idempotency_key": f"gate2r1-rights-{primary_item['source_version_id']}-{register['manifest_sha256'][:12]}",
    }
    inventory_version = {
        "inventory_version_id": inventory_version_id,
        "inventory_code": register["inventory_code"],
        "version_number": register["version_number"],
        "curriculum": scope["curriculum"],
        "grade": scope["grade"],
        "subject": scope["subject"],
        "delivery_languages": scope["delivery_languages"],
        "terms": scope["terms"],
        "strands": scope["strands"],
        "status": register["status"],
        "manifest_sha256": register["manifest_sha256"],
        "frozen_by": register["frozen_by"],
        "frozen_at": parse_timestamp(register["frozen_at"]),
        "created_by": CREATED_BY,
    }
    inventory_items = []
    for item in register["items"]:
        item_evidence = dict(item.get("evidence") or {})
        if item.get("item_status") == "absence_approved":
            item_evidence["registered_source_id"] = item.get("source_id")
            item_evidence["registered_source_version_id"] = item.get("source_version_id")
        inventory_items.append(
            {
                "inventory_item_id": uuid.uuid5(
                    LOADER_NAMESPACE,
                    f"inventory-item:{inventory_version_id}:{item['requirement_code']}",
                ),
                "inventory_version_id": inventory_version_id,
                "requirement_code": item["requirement_code"],
                "requirement_type": item["requirement_type"],
                "authority_tier": item["authority_tier"],
                "term": item.get("term"),
                "strand": item.get("strand"),
                "language": item.get("language"),
                "source_id": uuid.UUID(item["source_id"]) if item.get("item_status") == "located" else None,
                "source_version_id": (
                    uuid.UUID(item["source_version_id"]) if item.get("item_status") == "located" else None
                ),
                "item_status": item["item_status"],
                "absence_reason": item.get("absence_reason"),
                "evidence": item_evidence,
                "reviewed_by": item.get("reviewed_by"),
                "reviewed_at": parse_timestamp(item["reviewed_at"]) if item.get("reviewed_at") else None,
            }
        )

    return {
        "source": source,
        "source_version": source_version,
        "rights_decision": rights_decision,
        "inventory_version": inventory_version,
        "inventory_items": inventory_items,
    }


def normalize_database_url(value: str) -> str:
    return value.replace("postgresql+asyncpg://", "postgresql://", 1)


async def insert_records(database_url: str, records: dict[str, Any]) -> dict[str, int]:
    import asyncpg

    conn = await asyncpg.connect(normalize_database_url(database_url))
    try:
        async with conn.transaction():
            source = records["source"]
            await conn.execute(
                """
                INSERT INTO curriculum_sources
                  (source_id,publisher,authority_tier,official_source_url,document_title,document_type,
                   country,curriculum,phase,grade,subject,language,created_by)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
                ON CONFLICT (source_id) DO NOTHING
                """,
                *source.values(),
            )
            version = records["source_version"]
            await conn.execute(
                """
                INSERT INTO curriculum_source_versions
                  (source_version_id,source_id,version_label,publication_date,effective_from,effective_to,
                   copyright_owner,original_sha256,original_object_uri,media_type,file_size_bytes,
                   retrieved_at,retrieval_metadata,created_by)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13::jsonb,$14)
                ON CONFLICT (source_version_id) DO NOTHING
                """,
                version["source_version_id"],
                version["source_id"],
                version["version_label"],
                version["publication_date"],
                version["effective_from"],
                version["effective_to"],
                version["copyright_owner"],
                version["original_sha256"],
                version["original_object_uri"],
                version["media_type"],
                version["file_size_bytes"],
                version["retrieved_at"],
                json.dumps(version["retrieval_metadata"], sort_keys=True),
                version["created_by"],
            )
            decision = records["rights_decision"]
            await conn.execute(
                """
                INSERT INTO curriculum_rights_decisions
                  (rights_decision_id,source_version_id,decision_status,may_store_original,may_extract,
                   may_embed,may_use_for_retrieval,may_include_in_model_prompt,may_generate_derivatives,
                   may_translate,may_publish_translation,may_show_excerpt_to_educator,
                   may_show_excerpt_to_learner,may_redistribute,may_use_commercially,
                   may_use_for_model_training,requires_attribution,conditions,decision_basis,evidence_uri,
                   reviewed_by,reviewed_at,expires_at,idempotency_key)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18::jsonb,$19,$20,$21,$22,$23,$24)
                ON CONFLICT (rights_decision_id) DO NOTHING
                """,
                decision["rights_decision_id"],
                decision["source_version_id"],
                decision["decision_status"],
                *(decision[field] for field in RIGHTS_FIELDS),
                json.dumps(decision["conditions"], sort_keys=True),
                decision["decision_basis"],
                decision["evidence_uri"],
                decision["reviewed_by"],
                decision["reviewed_at"],
                decision["expires_at"],
                decision["idempotency_key"],
            )
            inventory = records["inventory_version"]
            await conn.execute(
                """
                INSERT INTO curriculum_inventory_versions
                  (inventory_version_id,inventory_code,version_number,curriculum,grade,subject,
                   delivery_languages,terms,strands,status,manifest_sha256,frozen_by,frozen_at,created_by)
                VALUES ($1,$2,$3,$4,$5,$6,$7::jsonb,$8::jsonb,$9::jsonb,$10,$11,$12,$13,$14)
                ON CONFLICT (inventory_version_id) DO NOTHING
                """,
                inventory["inventory_version_id"],
                inventory["inventory_code"],
                inventory["version_number"],
                inventory["curriculum"],
                inventory["grade"],
                inventory["subject"],
                json.dumps(inventory["delivery_languages"]),
                json.dumps(inventory["terms"]),
                json.dumps(inventory["strands"]),
                inventory["status"],
                inventory["manifest_sha256"],
                inventory["frozen_by"],
                inventory["frozen_at"],
                inventory["created_by"],
            )
            for item in records["inventory_items"]:
                await conn.execute(
                    """
                    INSERT INTO curriculum_inventory_items
                      (inventory_item_id,inventory_version_id,requirement_code,requirement_type,authority_tier,
                       term,strand,language,source_id,source_version_id,item_status,absence_reason,evidence,
                       reviewed_by,reviewed_at)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13::jsonb,$14,$15)
                    ON CONFLICT (inventory_item_id) DO NOTHING
                    """,
                    item["inventory_item_id"],
                    item["inventory_version_id"],
                    item["requirement_code"],
                    item["requirement_type"],
                    item["authority_tier"],
                    item["term"],
                    item["strand"],
                    item["language"],
                    item["source_id"],
                    item["source_version_id"],
                    item["item_status"],
                    item["absence_reason"],
                    json.dumps(item["evidence"], sort_keys=True),
                    item["reviewed_by"],
                    item["reviewed_at"],
                )

            await verify_persisted_records(conn, records)
            counts = await conn.fetchrow(
                """
                SELECT
                  (SELECT count(*) FROM curriculum_sources WHERE source_id=$1) AS sources,
                  (SELECT count(*) FROM curriculum_source_versions WHERE source_version_id=$2) AS source_versions,
                  (SELECT count(*) FROM curriculum_rights_decisions WHERE rights_decision_id=$3) AS rights_decisions,
                  (SELECT count(*) FROM curriculum_inventory_versions WHERE inventory_version_id=$4) AS inventory_versions,
                  (SELECT count(*) FROM curriculum_inventory_items WHERE inventory_version_id=$4) AS inventory_items
                """,
                records["source"]["source_id"],
                records["source_version"]["source_version_id"],
                records["rights_decision"]["rights_decision_id"],
                records["inventory_version"]["inventory_version_id"],
            )
            result = dict(counts)
            expected = {
                "sources": 1,
                "source_versions": 1,
                "rights_decisions": 1,
                "inventory_versions": 1,
                "inventory_items": len(records["inventory_items"]),
            }
            if result != expected:
                raise RuntimeError(f"authority record count mismatch: expected {expected}, got {result}")
            return result
    finally:
        await conn.close()


async def verify_persisted_records(conn: Any, records: dict[str, Any]) -> None:
    source = records["source"]
    persisted_source = await conn.fetchrow(
        """
        SELECT source_id,publisher,authority_tier,official_source_url,document_title,document_type,
               country,curriculum,phase,grade,subject,language,created_by
        FROM curriculum_sources
        WHERE source_id=$1
        """,
        source["source_id"],
    )
    if persisted_source is None:
        raise RuntimeError("loaded curriculum_sources row is missing")
    assert_field_match("curriculum_sources", dict(persisted_source), source)

    version = records["source_version"]
    persisted_version = await conn.fetchrow(
        """
        SELECT source_version_id,source_id,version_label,publication_date,effective_from,effective_to,
               copyright_owner,original_sha256,original_object_uri,media_type,file_size_bytes,
               retrieved_at,retrieval_metadata,created_by
        FROM curriculum_source_versions
        WHERE source_version_id=$1
        """,
        version["source_version_id"],
    )
    if persisted_version is None:
        raise RuntimeError("loaded curriculum_source_versions row is missing")
    actual_version = dict(persisted_version)
    actual_version["retrieval_metadata"] = jsonb_value(actual_version["retrieval_metadata"])
    assert_field_match("curriculum_source_versions", actual_version, version)

    decision = records["rights_decision"]
    persisted_decision = await conn.fetchrow(
        f"""
        SELECT rights_decision_id,source_version_id,decision_status,{','.join(RIGHTS_FIELDS)},
               conditions,decision_basis,evidence_uri,reviewed_by,reviewed_at,expires_at,idempotency_key
        FROM curriculum_rights_decisions
        WHERE rights_decision_id=$1
        """,
        decision["rights_decision_id"],
    )
    if persisted_decision is None:
        raise RuntimeError("loaded curriculum_rights_decisions row is missing")
    actual_decision = dict(persisted_decision)
    actual_decision["conditions"] = jsonb_value(actual_decision["conditions"])
    assert_field_match("curriculum_rights_decisions", actual_decision, decision)

    inventory = records["inventory_version"]
    persisted_inventory = await conn.fetchrow(
        """
        SELECT inventory_version_id,inventory_code,version_number,curriculum,grade,subject,
               delivery_languages,terms,strands,status,manifest_sha256,frozen_by,frozen_at,created_by
        FROM curriculum_inventory_versions
        WHERE inventory_version_id=$1
        """,
        inventory["inventory_version_id"],
    )
    if persisted_inventory is None:
        raise RuntimeError("loaded curriculum_inventory_versions row is missing")
    actual_inventory = dict(persisted_inventory)
    for field in ("delivery_languages", "terms", "strands"):
        actual_inventory[field] = jsonb_value(actual_inventory[field])
    assert_field_match("curriculum_inventory_versions", actual_inventory, inventory)

    expected_items = {item["requirement_code"]: item for item in records["inventory_items"]}
    persisted_items = await conn.fetch(
        """
        SELECT inventory_item_id,inventory_version_id,requirement_code,requirement_type,authority_tier,
               term,strand,language,source_id,source_version_id,item_status,absence_reason,evidence,
               reviewed_by,reviewed_at
        FROM curriculum_inventory_items
        WHERE inventory_version_id=$1
        ORDER BY requirement_code
        """,
        inventory["inventory_version_id"],
    )
    actual_codes = {row["requirement_code"] for row in persisted_items}
    expected_codes = set(expected_items)
    if actual_codes != expected_codes:
        raise RuntimeError(
            "curriculum_inventory_items requirement-code mismatch: "
            f"expected_hash={field_hash({'codes': sorted(expected_codes)})} "
            f"actual_hash={field_hash({'codes': sorted(actual_codes)})}"
        )
    for row in persisted_items:
        actual_item = dict(row)
        actual_item["evidence"] = jsonb_value(actual_item["evidence"])
        assert_field_match(
            f"curriculum_inventory_items[{row['requirement_code']}]",
            actual_item,
            expected_items[row["requirement_code"]],
        )


def serializable_summary(records: dict[str, Any], counts: dict[str, int] | None, *, downloaded: bool) -> dict[str, Any]:
    retrieval_metadata = records["source_version"]["retrieval_metadata"]
    source_manifest_path = ROOT / retrieval_metadata["source_manifest_path"]
    return {
        "valid": True,
        "downloaded_source": downloaded,
        "source_verified_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_manifest_sha256": sha256_file(source_manifest_path),
        "source_manifest_path": retrieval_metadata["source_manifest_path"],
        "source_path": retrieval_metadata["source_path"],
        "canonical_source_url": retrieval_metadata["canonical_source_url"],
        "object_store_uri": retrieval_metadata["object_store_uri"],
        "source_id": str(records["source"]["source_id"]),
        "source_version_id": str(records["source_version"]["source_version_id"]),
        "rights_decision_id": str(records["rights_decision"]["rights_decision_id"]),
        "inventory_version_id": str(records["inventory_version"]["inventory_version_id"]),
        "source_sha256": records["source_version"]["original_sha256"],
        "file_size_bytes": records["source_version"]["file_size_bytes"],
        "inventory_items": len(records["inventory_items"]),
        "counts": counts,
        "status": "loaded" if counts is not None else "validated",
    }


async def async_main(args: argparse.Namespace) -> dict[str, Any]:
    register = load_register(args.register)
    source_manifest = read_json(args.source_manifest)
    source_document = source_manifest_document(source_manifest)
    source_path, file_size, checksum, downloaded = ensure_verified_source_file(
        source_document,
        download_missing=args.download_missing,
    )
    records = build_records(
        register,
        source_document,
        source_path=source_path,
        file_size_bytes=file_size,
        source_sha256=checksum,
        downloaded=downloaded,
    )
    counts = None
    if not args.dry_run:
        database_url = args.database_url
        if not database_url:
            raise RuntimeError("database URL is required unless --dry-run is set")
        counts = await insert_records(database_url, records)
    return serializable_summary(records, counts, downloaded=downloaded)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST)
    parser.add_argument("--database-url", default=None)
    parser.add_argument("--download-missing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.database_url is None:
        import os

        args.database_url = os.getenv("PHASE02R_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")

    try:
        result = asyncio.run(async_main(args))
    except Exception as exc:
        if args.json:
            print(json.dumps({"valid": False, "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"Gate 2R.1 authority record loading failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            "Gate 2R.1 authority records "
            f"{result['status']}: source={result['source_id']} version={result['source_version_id']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
