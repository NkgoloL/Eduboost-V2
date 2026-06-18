from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv("PHASE02R_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="PHASE02R_TEST_DATABASE_URL is required")


@pytest.fixture
async def session():
    engine = create_async_engine(DATABASE_URL)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as db:
        yield db
        await db.rollback()
    await engine.dispose()


@pytest.mark.asyncio
async def test_phase02r_tables_columns_and_append_only_triggers_exist(session):
    expected_tables = {
        "curriculum_sources",
        "curriculum_source_versions",
        "curriculum_rights_decisions",
        "curriculum_inventory_versions",
        "curriculum_inventory_items",
        "curriculum_review_decisions",
    }
    tables = {
        row[0]
        for row in (
            await session.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_name LIKE 'curriculum_%'"
                )
            )
        ).all()
    }
    assert expected_tables.issubset(tables)

    columns = {
        row[0]
        for row in (
            await session.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema='public' AND table_name='curriculum_rights_decisions'"
                )
            )
        ).all()
    }
    assert {"may_translate", "may_publish_translation", "may_use_for_model_training", "conditions"}.issubset(columns)

    inventory_columns = {
        row[0]
        for row in (
            await session.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema='public' AND table_name='curriculum_inventory_items'"
                )
            )
        ).all()
    }
    assert {"source_id", "source_version_id"}.issubset(inventory_columns)

    triggers = {
        row[0]
        for row in (
            await session.execute(
                text(
                    "SELECT tgname FROM pg_trigger "
                    "WHERE NOT tgisinternal AND tgname LIKE 'trg_curriculum_%_append_only'"
                )
            )
        ).all()
    }
    assert {f"trg_{name}_append_only" for name in expected_tables}.issubset(triggers)


@pytest.mark.asyncio
async def test_authority_rows_are_append_only(session):
    source_id = uuid.uuid4()
    source_version_id = uuid.uuid4()
    await session.execute(
        text(
            "INSERT INTO curriculum_sources "
            "(source_id,publisher,authority_tier,document_title,document_type,country,curriculum,grade,subject,language,created_by) "
            "VALUES (:id,'DBE','tier_1','CAPS Grade 4 Mathematics','policy','ZA','CAPS',4,'Mathematics','en','test')"
        ),
        {"id": source_id},
    )
    await session.execute(
        text(
            "INSERT INTO curriculum_source_versions "
            "(source_version_id,source_id,version_label,original_sha256,original_object_uri,media_type,file_size_bytes,retrieved_at,retrieval_metadata,created_by) "
            "VALUES (:version_id,:source_id,'v1',:sha,'s3://test/source.pdf','application/pdf',10,now(),'{}'::jsonb,'test')"
        ),
        {"version_id": source_version_id, "source_id": source_id, "sha": "a" * 64},
    )
    await session.execute(
        text(
            "INSERT INTO curriculum_rights_decisions "
            "(source_version_id,decision_status,may_store_original,may_extract,may_embed,may_use_for_retrieval,"
            "may_include_in_model_prompt,may_generate_derivatives,may_translate,may_publish_translation,"
            "may_show_excerpt_to_educator,may_show_excerpt_to_learner,may_redistribute,may_use_commercially,"
            "may_use_for_model_training,requires_attribution,conditions,decision_basis,evidence_uri,reviewed_by,reviewed_at,idempotency_key) "
            "VALUES (:version_id,'approved',true,true,true,true,true,true,true,false,true,false,false,false,false,true,"
            "'{}'::jsonb,'written permission','evidence://rights/test','reviewer',now(),'rights-test')"
        ),
        {"version_id": source_version_id},
    )
    await session.commit()

    for table_name, predicate in (
        ("curriculum_sources", "source_id=:id"),
        ("curriculum_source_versions", "source_version_id=:id"),
        ("curriculum_rights_decisions", "source_version_id=:id"),
    ):
        identifier = source_id if table_name == "curriculum_sources" else source_version_id
        with pytest.raises(DBAPIError):
            await session.execute(
                text(f"UPDATE {table_name} SET created_at=created_at WHERE {predicate}"),
                {"id": identifier},
            )
            await session.flush()
        await session.rollback()


@pytest.mark.asyncio
async def test_conditional_rights_require_structured_conditions(session):
    source_id = uuid.uuid4()
    source_version_id = uuid.uuid4()
    await session.execute(
        text(
            "INSERT INTO curriculum_sources "
            "(source_id,publisher,authority_tier,document_title,document_type,country,curriculum,grade,subject,language,created_by) "
            "VALUES (:id,'DBE','tier_1','Conditional source','policy','ZA','CAPS',4,'Mathematics','en','test')"
        ),
        {"id": source_id},
    )
    await session.execute(
        text(
            "INSERT INTO curriculum_source_versions "
            "(source_version_id,source_id,version_label,original_sha256,original_object_uri,media_type,file_size_bytes,retrieved_at,retrieval_metadata,created_by) "
            "VALUES (:version_id,:source_id,'v1',:sha,'s3://test/conditional.pdf','application/pdf',10,now(),'{}'::jsonb,'test')"
        ),
        {"version_id": source_version_id, "source_id": source_id, "sha": "b" * 64},
    )
    with pytest.raises(IntegrityError):
        await session.execute(
            text(
                "INSERT INTO curriculum_rights_decisions "
                "(source_version_id,decision_status,conditions,decision_basis,evidence_uri,reviewed_by,reviewed_at,idempotency_key) "
                "VALUES (:version_id,'approved_with_conditions','{}'::jsonb,'basis','evidence://rights/conditional','reviewer',now(),'conditional-test')"
            ),
            {"version_id": source_version_id},
        )
        await session.flush()
    await session.rollback()
