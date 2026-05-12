"""
conftest.py – diagnostics unit test package
============================================
Provides a safe, skip-on-unavailable database fixture so that
tests/unit/modules/diagnostics/ never hard-fail with
ConnectionRefusedError when a local Postgres instance is absent.

Design decisions
----------------
* The fixture is *not* autouse.  Individual tests that genuinely need a
  live DB must opt in with @pytest.mark.usefixtures("db_session") or by
  declaring the fixture as a parameter.  Pure unit tests remain completely
  unaffected.
* When Postgres is unavailable the fixture skips cleanly via
  pytest.skip(), which surfaces as an 's' in the test run rather than
  an 'E' (setup error).  This keeps the aggregate unit gate green.
* Integration-class tests that must assert real persistence behaviour
  should be moved to tests/integration/ and run against a guaranteed DB
  (docker-compose service or CI service container).  See the companion
  file tests/integration/modules/diagnostics/conftest.py.
"""

from __future__ import annotations

import socket
import os

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _postgres_is_reachable() -> bool:
    """Return True when a TCP connection to the configured Postgres host/port
    succeeds within 1 second."""
    host = os.environ.get("PGHOST", "127.0.0.1")
    port = int(os.environ.get("PGPORT", "5432"))
    try:
        with socket.create_connection((host, port), timeout=1.0):
            return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Markers
# ---------------------------------------------------------------------------

def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "requires_db: mark test as requiring a live Postgres instance "
        "(skipped automatically in unit runs when DB is unavailable).",
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def db_available() -> bool:
    """Module-scoped boolean – True when Postgres is reachable."""
    return _postgres_is_reachable()


@pytest.fixture(scope="module")
def skip_if_no_db(db_available: bool) -> None:
    """Opt-in fixture: skip the entire module when Postgres is absent.

    Usage (at module level in a test file):
        pytestmark = pytest.mark.usefixtures("skip_if_no_db")

    Or per-test:
        def test_something(skip_if_no_db, ...):
            ...
    """
    if not db_available:
        pytest.skip(
            "Postgres not reachable – skipping DB-dependent test "
            "(move to tests/integration/ for guaranteed execution)."
        )


@pytest.fixture(scope="function")
def db_session(skip_if_no_db):  # noqa: F811
    """Function-scoped SQLAlchemy session backed by a real Postgres DB.

    Rolls back after every test to keep the DB clean without truncating
    tables.  Skips automatically when Postgres is unavailable.

    Replace the engine/session construction below with your project's
    actual session factory (e.g. from app.core.database).
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:5432/eduboost_test",
    )

    engine = create_engine(database_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.begin_nested()          # savepoint so rollback is cheap

    yield session

    session.rollback()
    session.close()
    engine.dispose()
