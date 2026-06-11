from backend.app.main import create_app
from backend.app.routes.health import read_health
from backend.app.routes.version import read_version


def test_app_registers_system_routes() -> None:
    app = create_app()

    paths = {getattr(route, "path", None) for route in app.routes}

    assert "/health" in paths
    assert "/version" in paths


def test_health_route_payload() -> None:
    assert read_health() == {"status": "ok"}


def test_version_route_payload() -> None:
    body = read_version()

    assert body["app"] == "open-health-server"
    assert body["version"] == "0.1.0"
    assert body["environment"] == "development"
