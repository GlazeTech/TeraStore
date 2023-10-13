from fastapi.testclient import TestClient

from api.main import create_app


def test_create_device() -> None:
    """Test that a device can be created."""
    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/devices/",
            json={"friendly_name": "Glaze I"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["friendly_name"] == "Glaze I"
        assert data["device_id"] is not None
