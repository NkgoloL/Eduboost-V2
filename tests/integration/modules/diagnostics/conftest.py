"""
tests/integration/modules/diagnostics/conftest.py
==================================================
Integration-tier fixtures for diagnostics tests.

Unlike the unit conftest, this fixture HARD-FAILS if Postgres is absent.
Integration tests are only run in environments (CI service containers,
local docker-compose) that guarantee a live database – there is no value
in silently skipping them there.

Add to CI with a dedicated job/step:
    pytest tests/integration/ -m "not e2e" --tb=short -q
"""

from __future__ import annotations

import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session


DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@127.0.0.1:5432/eduboost_test",
)


@pytest.fixture(scope="session")
def integration_engine():
    """Session-scoped engine – created once per pytest session."""
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(integration_engine) -> Session:
    """Function-scoped session wrapped in a savepoint that is always
    rolled back, leaving the DB clean between tests."""
    connection = integration_engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    # Use a nested transaction (SAVEPOINT) so individual tests can commit
    # without affecting the outer transaction that we roll back.
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
