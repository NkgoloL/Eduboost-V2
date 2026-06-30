from __future__ import annotations
import fnmatch

import pytest
pytestmark = pytest.mark.integration


import pytest_asyncio


@pytest_asyncio.fixture(scope="session", autouse=True)
async def integration_db(test_db_setup):
    """Automatically create and tear down the test database schema for integration tests."""
    yield


@pytest_asyncio.fixture(scope="session")
def fake_redis():
    """In-process async Redis substitute for integration tests."""
    try:
        import fakeredis.aioredis as fakeredis

        server = fakeredis.FakeServer()
        return fakeredis.FakeRedis(server=server)
    except ImportError:
        store: dict[str, str] = {}

        class _FakeRedis:
            async def get(self, key):
                return store.get(key)

            async def set(self, key, value, ex=None):
                store[key] = value
                return True

            async def delete(self, *keys):
                deleted = 0
                for key in keys:
                    if key in store:
                        del store[key]
                        deleted += 1
                return deleted

            async def scan_iter(self, match=None):
                for key in list(store.keys()):
                    if match is None or fnmatch.fnmatch(key, match):
                        yield key

            async def ttl(self, key):
                return -1

            def pipeline(self):
                self._queue = []
                return self

            async def execute(self):
                results = []
                for cmd, args in self._queue:
                    if cmd == "incr":
                        results.append(await self._incr_immediate(*args))
                    elif cmd == "expire":
                        results.append(await self._expire_immediate(*args))
                self._queue = []
                return results

            def incr(self, key):
                if hasattr(self, "_queue") and self._queue is not None:
                    self._queue.append(("incr", (key,)))
                    return self
                return self._incr_immediate(key)

            async def _incr_immediate(self, key):
                val = int(store.get(key, 0)) + 1
                store[key] = str(val)
                return val

            def expire(self, key, seconds):
                if hasattr(self, "_queue") and self._queue is not None:
                    self._queue.append(("expire", (key, seconds)))
                    return self
                return self._expire_immediate(key, seconds)

            async def _expire_immediate(self, key, seconds):
                return True

        return _FakeRedis()


@pytest.fixture(autouse=True)
def patch_redis(monkeypatch, fake_redis):
    """Patch application redis access to use fake Redis for integration tests."""
    import app.core.redis as redis_module
    import app.core.refresh_tokens as refresh_tokens_module

    monkeypatch.setattr(redis_module, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(refresh_tokens_module, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(redis_module, "_pool", fake_redis)
    yield


@pytest_asyncio.fixture
async def seed_consent():
    """Compatibility fixture placeholder for older integration tests."""
    yield
