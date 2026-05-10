def test_import_api_modules():
    # Minimal import smoke test to ensure backend modules import cleanly
    import importlib

    modules = [
        "app.api_v2",
        "app.api_v2_routers",
        "app.core.config",
        "app.models",
        "app.repositories",
        "app.services",
    ]

    for m in modules:
        importlib.import_module(m)
