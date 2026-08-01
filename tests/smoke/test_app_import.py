def test_fastapi_app_imports():
    from app.api_v2 import app

    route_paths = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/health" in route_paths
