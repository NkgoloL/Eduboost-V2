from __future__ import annotations

import hashlib
import os
import secrets
import uuid

import asyncpg
import pytest

pytestmark = pytest.mark.integration


def _dsn() -> str:
    return os.getenv("AUTH_REFRESH_DB_PROOF_DSN", "").strip()


def test_auth_refresh_db_proof_requires_explicit_dsn():
    assert _dsn(), "AUTH_REFRESH_DB_PROOF_DSN must be set for DB-backed proof"


def _asyncpg_dsn() -> str:
    return _dsn().replace("postgresql+asyncpg://", "postgresql://", 1)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def _issue_token(conn: asyncpg.Connection, *, run_id: str, user_id: str, family_id: str) -> str:
    token = f"refresh-db-proof-{secrets.token_urlsafe(24)}"
    await conn.execute(
        """
        INSERT INTO auth_refresh_db_proof_tokens (run_id, user_id, family_id, token_hash)
        VALUES ($1, $2, $3, $4)
        """,
        run_id,
        user_id,
        family_id,
        _token_hash(token),
    )
    return token


async def _consume_token(conn: asyncpg.Connection, *, run_id: str, token: str) -> str:
    token_hash = _token_hash(token)
    row = await conn.fetchrow(
        """
        SELECT user_id, family_id, consumed_at, revoked_at
        FROM auth_refresh_db_proof_tokens
        WHERE run_id = $1 AND token_hash = $2
        """,
        run_id,
        token_hash,
    )
    if row is None:
        raise AssertionError("refresh token was not persisted")
    if row["revoked_at"] is not None:
        raise AssertionError("refresh token was revoked")
    if row["consumed_at"] is not None:
        await conn.execute(
            """
            UPDATE auth_refresh_db_proof_tokens
            SET revoked_at = COALESCE(revoked_at, now())
            WHERE run_id = $1 AND family_id = $2
            """,
            run_id,
            row["family_id"],
        )
        raise AssertionError("refresh token reuse detected")

    await conn.execute(
        """
        UPDATE auth_refresh_db_proof_tokens
        SET consumed_at = now()
        WHERE run_id = $1 AND token_hash = $2
        """,
        run_id,
        token_hash,
    )
    return await _issue_token(conn, run_id=run_id, user_id=row["user_id"], family_id=row["family_id"])


@pytest.mark.asyncio
async def test_refresh_persistence_logout_revoke_reuse_db_proof_contract():
    assert os.getenv("AUTH_REFRESH_DB_PROOF_ENABLED") == "1"
    assert _dsn(), "DB proof DSN missing"

    run_id = f"auth-refresh-db-proof-{uuid.uuid4()}"
    user_id = f"user-{uuid.uuid4()}"
    family_id = f"family-{uuid.uuid4()}"
    conn = await asyncpg.connect(_asyncpg_dsn())
    try:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS auth_refresh_db_proof_tokens (
                id bigserial PRIMARY KEY,
                run_id text NOT NULL,
                user_id text NOT NULL,
                family_id text NOT NULL,
                token_hash text NOT NULL,
                consumed_at timestamptz NULL,
                revoked_at timestamptz NULL,
                created_at timestamptz NOT NULL DEFAULT now(),
                UNIQUE (run_id, token_hash)
            )
            """
        )

        refresh_token = await _issue_token(conn, run_id=run_id, user_id=user_id, family_id=family_id)
        persisted = await conn.fetchval(
            "SELECT count(*) FROM auth_refresh_db_proof_tokens WHERE run_id = $1 AND token_hash = $2",
            run_id,
            _token_hash(refresh_token),
        )
        assert persisted == 1

        await conn.execute(
            """
            UPDATE auth_refresh_db_proof_tokens
            SET revoked_at = now()
            WHERE run_id = $1 AND token_hash = $2
            """,
            run_id,
            _token_hash(refresh_token),
        )
        with pytest.raises(AssertionError, match="revoked"):
            await _consume_token(conn, run_id=run_id, token=refresh_token)

        token_a = await _issue_token(conn, run_id=run_id, user_id=user_id, family_id=family_id)
        token_b = await _issue_token(conn, run_id=run_id, user_id=user_id, family_id=family_id)
        await conn.execute(
            "UPDATE auth_refresh_db_proof_tokens SET revoked_at = now() WHERE run_id = $1 AND user_id = $2",
            run_id,
            user_id,
        )
        active_after_revoke_all = await conn.fetchval(
            """
            SELECT count(*) FROM auth_refresh_db_proof_tokens
            WHERE run_id = $1 AND user_id = $2 AND revoked_at IS NULL
            """,
            run_id,
            user_id,
        )
        assert active_after_revoke_all == 0
        for token in (token_a, token_b):
            with pytest.raises(AssertionError, match="revoked"):
                await _consume_token(conn, run_id=run_id, token=token)

        reusable_token = await _issue_token(conn, run_id=run_id, user_id=user_id, family_id=family_id)
        rotated_token = await _consume_token(conn, run_id=run_id, token=reusable_token)
        assert rotated_token != reusable_token
        consumed_at = await conn.fetchval(
            "SELECT consumed_at FROM auth_refresh_db_proof_tokens WHERE run_id = $1 AND token_hash = $2",
            run_id,
            _token_hash(reusable_token),
        )
        assert consumed_at is not None
        with pytest.raises(AssertionError, match="reuse detected"):
            await _consume_token(conn, run_id=run_id, token=reusable_token)
        family_active = await conn.fetchval(
            """
            SELECT count(*) FROM auth_refresh_db_proof_tokens
            WHERE run_id = $1 AND family_id = $2 AND revoked_at IS NULL
            """,
            run_id,
            family_id,
        )
        assert family_active == 0
    finally:
        await conn.execute("DELETE FROM auth_refresh_db_proof_tokens WHERE run_id = $1", run_id)
        await conn.close()
