from fastapi.testclient import TestClient

from api.public.device.models import DeviceCreate


def test_create_device(client: TestClient) -> None:
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
    response = client.get("/devices/abc")
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid integer"
    assert data["detail"][0]["type"] == "type_error.integer"


def test_get_device_with_nonexistent_device_id(client: TestClient) -> None:
    response = client.get("/devices/10000000")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Device not found with id: 10000000"


def test_get_all_devices(client: TestClient) -> None:
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
    response = client.get("/devices/?limit=abc")
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid integer"
    assert data["detail"][0]["type"] == "type_error.integer"


def test_get_all_devices_with_offset(client: TestClient) -> None:
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
    response = client.get("/devices/?offset=abc")
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid integer"
    assert data["detail"][0]["type"] == "type_error.integer"


def test_get_all_devices_with_limit_and_offset(client: TestClient) -> None:
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
    response = client.get("/devices/?limit=abc&offset=abc")
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid integer"
    assert data["detail"][0]["type"] == "type_error.integer"
    assert data["detail"][1]["msg"] == "value is not a valid integer"
    assert data["detail"][1]["type"] == "type_error.integer"
