import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from tests.phase02.test_phase2_postgres_integration import seed_corpus

async def main():
    engine = create_async_engine(os.environ["DATABASE_URL"])
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await session.execute(text("TRUNCATE retrieval_source_chunks, retrieval_source_documents CASCADE"))
        await seed_corpus(session)
        await session.commit()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
