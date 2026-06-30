import pytest

from app.services import launch_content_seed


@pytest.mark.asyncio
async def test_startup_seed_disabled_by_default(monkeypatch) -> None:
    called = False
    async def fail_if_called():
        nonlocal called
        called = True
    monkeypatch.setattr(launch_content_seed, "_try_advisory_lock", fail_if_called)
    monkeypatch.setattr(launch_content_seed.settings, "CONTENT_STARTUP_SEED_ENABLED", False)
    await launch_content_seed.seed_launch_content_if_needed()
    assert called is False
