#!/usr/bin/env python
"""Re-embed one approved retrieval document with the configured provider."""
from __future__ import annotations

import argparse
import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.services.semantic_retrieval import RetrievalIndexingService, build_embedding_provider


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("document_id")
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            service = RetrievalIndexingService(
                embedding_provider=build_embedding_provider()
            )
            count = await service.reindex_document(
                session, document_id=args.document_id
            )
            await session.commit()
    except Exception:
        raise
    finally:
        await engine.dispose()
    print(f"Reindexed {count} chunks for {args.document_id}")
    return 0 if count else 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
