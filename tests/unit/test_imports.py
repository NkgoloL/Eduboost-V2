def test_import_api_modules():
    # Minimal import smoke test to ensure backend modules import cleanly
    import importlib

    modules = [
        "app.api_v2",
        "app.api_v2_routers",
        "app.api.main",
        "app.api.core.config",
        "app.api.models.db_models",
    ]

    for m in modules:
        importlib.import_module(m)
