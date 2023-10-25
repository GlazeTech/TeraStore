from fastapi.testclient import TestClient

from api.public.device.models import DeviceCreate


def test_create_device(client: TestClient) -> None:
    """Test creating a device.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    device = DeviceCreate.create_mock(friendly_name="Glaze I")
    response = client.post(
        "/devices/",
        json=device.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["friendly_name"] == "Glaze I"
    assert data["device_id"] is not None
