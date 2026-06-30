from app.api_v2 import ROUTER_REGISTRY, app


def test_tutor_router_registered_once():
    names = [name for name, _router in ROUTER_REGISTRY]
    assert names.count("tutor") == 1
    paths = [route.path for route in app.routes]
    expected = {
        "/api/v2/tutor/sessions",
        "/api/v2/tutor/sessions/{session_id}",
        "/api/v2/tutor/sessions/{session_id}/messages",
        "/api/v2/tutor/sessions/{session_id}/messages/stream",
        "/api/v2/tutor/sessions/{session_id}/cancel",
    }
    assert expected <= set(paths)
