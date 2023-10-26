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
    device_payload = {"friendly_name": "Glaze I"}
    response = client.post(
        "/devices/",
        json=device_payload,
    )
    data = response.json()

    assert response.status_code == 200
    assert data["friendly_name"] == "Glaze I"
    assert data["device_id"] is not None


def test_create_device_with_invalid_friendly_name(client: TestClient) -> None:
    """Test creating a device with an invalid friendly name.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    device_payload = {"friendly_name": [1]}
    response = client.post(
        "/devices/",
        json=device_payload,
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "str type expected"
    assert data["detail"][0]["type"] == "type_error.str"


def test_create_device_with_extra_params(client: TestClient) -> None:
    """Test creating a device with extra parameters.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    device_payload = {"friendly_name": "Glaze I", "device_id": "abc"}
    response = client.post(
        "/devices/",
        json=device_payload,
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "extra fields not permitted"
    assert data["detail"][0]["type"] == "value_error.extra"


def test_create_device_with_empty_body(client: TestClient) -> None:
    """Test creating a device with an empty body.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    device_payload: dict[None, None] = {}
    response = client.post(
        "/devices/",
        json=device_payload,
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "field required"
    assert data["detail"][0]["type"] == "value_error.missing"


def test_create_device_with_invalid_device_id(client: TestClient) -> None:
    """Test creating a device with an invalid device id.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    device_payload = {
        "friendly_name": "Glaze I",
        "device_id": "00000000-0000-0000-0000-000000000000",
    }
    response = client.post(
        "/devices/",
        json=device_payload,
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "extra fields not permitted"
    assert data["detail"][0]["type"] == "value_error.extra"


def test_get_device(client: TestClient) -> None:
    """Test getting a device.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    device_payload = {"friendly_name": "Glaze I"}
    response = client.post(
        "/devices/",
        json=device_payload,
    )
    data = response.json()

    assert response.status_code == 200
    assert data["friendly_name"] == "Glaze I"
    assert data["device_id"] is not None

    device_id = data["device_id"]
    response = client.get(f"/devices/{device_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["friendly_name"] == "Glaze I"
    assert data["device_id"] == device_id


def test_get_device_with_invalid_device_id(client: TestClient) -> None:
    """Test getting a device with an invalid device id.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    response = client.get("/devices/abc")
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid uuid"
    assert data["detail"][0]["type"] == "type_error.uuid"


def test_get_device_with_nonexistent_device_id(client: TestClient) -> None:
    """Test getting a device with a nonexistent device id.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    response = client.get("/devices/00000000-0000-0000-0000-000000000000")
    data = response.json()

    assert response.status_code == 404
    assert (
        data["detail"]
        == "Device not found with id: 00000000-0000-0000-0000-000000000000"
    )


def test_get_all_devices(client: TestClient) -> None:
    """Test getting all devices.

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

    device = DeviceCreate.create_mock(friendly_name="Glaze II")
    response = client.post(
        "/devices/",
        json=device.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["friendly_name"] == "Glaze II"
    assert data["device_id"] is not None

    response = client.get("/devices/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["friendly_name"] == "Glaze I"
    assert data[0]["device_id"] is not None
    assert data[1]["friendly_name"] == "Glaze II"
    assert data[1]["device_id"] is not None


def test_get_all_devices_with_limit(client: TestClient) -> None:
    """Test getting all devices with a limit.

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

    device = DeviceCreate.create_mock(friendly_name="Glaze II")
    response = client.post(
        "/devices/",
        json=device.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["friendly_name"] == "Glaze II"
    assert data["device_id"] is not None

    response = client.get("/devices/?limit=1")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["friendly_name"] == "Glaze I"
    assert data[0]["device_id"] is not None


def test_get_all_devices_with_invalid_limit(client: TestClient) -> None:
    """Test getting all devices with an invalid limit.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    response = client.get("/devices/?limit=abc")
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid integer"
    assert data["detail"][0]["type"] == "type_error.integer"


def test_get_all_devices_with_offset(client: TestClient) -> None:
    """Test getting all devices with an offset.

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

    device = DeviceCreate.create_mock(friendly_name="Glaze II")
    response = client.post(
        "/devices/",
        json=device.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["friendly_name"] == "Glaze II"
    assert data["device_id"] is not None

    response = client.get("/devices/?offset=1")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["friendly_name"] == "Glaze II"
    assert data[0]["device_id"] is not None


def test_get_all_devices_with_invalid_offset(client: TestClient) -> None:
    """Test getting all devices with an invalid offset.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    response = client.get("/devices/?offset=abc")
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid integer"
    assert data["detail"][0]["type"] == "type_error.integer"


def test_get_all_devices_with_limit_and_offset(client: TestClient) -> None:
    """Test getting all devices with a limit and offset.

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

    device = DeviceCreate.create_mock(friendly_name="Glaze II")
    response = client.post(
        "/devices/",
        json=device.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["friendly_name"] == "Glaze II"
    assert data["device_id"] is not None

    response = client.get("/devices/?limit=1&offset=1")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["friendly_name"] == "Glaze II"
    assert data[0]["device_id"] is not None


def test_get_all_devices_with_invalid_limit_and_offset(client: TestClient) -> None:
    """Test getting all devices with an invalid limit and offset.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    response = client.get("/devices/?limit=abc&offset=abc")
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid integer"
    assert data["detail"][0]["type"] == "type_error.integer"
    assert data["detail"][1]["msg"] == "value is not a valid integer"
    assert data["detail"][1]["type"] == "type_error.integer"
