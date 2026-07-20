#!/usr/bin/env python
"""Import approved chunks from the existing SQLite ETL store into PostgreSQL retrieval.

The importer never promotes document status. It copies only rows already marked
approved/indexed/training_ready and preserves document/chunk version and checksum
metadata. Run it against a backup-tested ETL database and a controlled target.
"""
from __future__ import annotations

import argparse
import asyncio
import sqlite3
from collections import defaultdict
from pathlib import Path

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.services.semantic_retrieval import (
    RetrievalIndexingService,
    SourceChunkInput,
    SourceDocumentInput,
    build_embedding_provider,
)

SEARCHABLE = ("approved", "indexed", "training_ready")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--etl-db", required=True, type=Path)
    parser.add_argument("--scope-id", required=True)
    parser.add_argument("--permission-scope", default="public")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_documents(path: Path) -> list[tuple[dict, list[dict]]]:
    if not path.exists():
        raise FileNotFoundError(path)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        placeholders = ",".join("?" for _ in SEARCHABLE)
        documents = [
            dict(row)
            for row in connection.execute(
                """SELECT * FROM documents
                WHERE processing_status IN (""" + placeholders + """)
                ORDER BY document_id""",
                SEARCHABLE,
            ).fetchall()
        ]
        chunks_by_document: dict[str, list[dict]] = defaultdict(list)
        for row in connection.execute(
            "SELECT * FROM document_chunks ORDER BY document_id, chunk_index"
        ).fetchall():
            chunks_by_document[str(row["document_id"])].append(dict(row))
        return [
            (document, chunks_by_document.get(str(document["document_id"]), []))
            for document in documents
            if chunks_by_document.get(str(document["document_id"]))
        ]
    finally:
        connection.close()


async def main() -> int:
    args = parse_args()
    payload = load_documents(args.etl_db)
    print(
        f"Eligible documents: {len(payload)}; chunks: "
        f"{sum(len(chunks) for _, chunks in payload)}"
    )
    if args.dry_run:
        return 0

    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    imported = 0
    try:
        async with factory() as session:
            service = RetrievalIndexingService(
                embedding_provider=build_embedding_provider()
            )
            for document, chunks in payload:
                await service.upsert_document(
                    session,
                    document=SourceDocumentInput(
                        document_id=str(document["document_id"]),
                        document_version_id=str(document.get("version") or "1.0"),
                        title=str(document["title"]),
                        scope_id=args.scope_id,
                        caps_ref=None,
                        grade=document.get("grade"),
                        subject_code=document.get("subject"),
                        language=str(document.get("language") or "en"),
                        status=str(document["processing_status"]),
                        permission_scope=args.permission_scope,
                        license_status=str(document.get("license_status") or "unknown"),
                        quality_score=float(document.get("quality_score") or 0),
                        source_uri=document.get("source_url"),
                        metadata={
                            "source_id": document.get("source_id"),
                            "document_type": document.get("document_type"),
                            "publisher": document.get("publisher"),
                            "checksum": document.get("checksum"),
                            "curriculum": document.get("curriculum"),
                        },
                    ),
                    chunks=[
                        SourceChunkInput(
                            chunk_id=str(chunk["chunk_id"]),
                            chunk_index=int(chunk["chunk_index"]),
                            content=str(chunk["content"]),
                            heading=chunk.get("heading"),
                            section_path=chunk.get("section_path"),
                            page_start=chunk.get("page_start"),
                            page_end=chunk.get("page_end"),
                            caps_ref=chunk.get("curriculum_code"),
                            curriculum_mapping_id=chunk.get("curriculum_code"),
                            metadata={
                                "chunk_type": chunk.get("chunk_type"),
                                "token_count": chunk.get("token_count"),
                                "parent_chunk_id": chunk.get("parent_chunk_id"),
                            },
                        )
                        for chunk in chunks
                    ],
                )
                imported += len(chunks)
            await session.commit()
    finally:
        await engine.dispose()
    print(f"Imported and indexed {imported} approved chunks")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
