from fastapi.testclient import TestClient


def test_create_device(client: TestClient) -> None:
    """Test that a device can be created."""
    response = client.post(
        "/devices/",
        json={"friendly_name": "Glaze I"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["friendly_name"] == "Glaze I"
    assert data["device_id"] is not None


def test_retrieve_device(client: TestClient) -> None:
    """Test that a device can be retrieved."""
    response = client.post(
        "/devices/",
        json={"friendly_name": "Glaze I"},
    )
    data = response.json()

    response = client.get(
        f"/devices/{data['device_id']}",
        params={"friendly_name": "Glaze I"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["friendly_name"] == "Glaze I"


def test_create_device_missing_name(client: TestClient) -> None:
    """Test that a device cannot be created without a friendly name."""
    response = client.post(
        "/devices/",
        json={},
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "field required"
