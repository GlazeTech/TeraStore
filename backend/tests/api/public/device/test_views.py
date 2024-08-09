from uuid import uuid4

from fastapi.testclient import TestClient

from api.public.device.models import DeviceCreate

G1_SERIAL_NUMBER = "G-0001"
G2_SERIAL_NUMBER = "G-0002"
SERIAL_NUMBER_KEY = "serial_number"


def test_create_device(client: TestClient) -> None:
    device_payload = {SERIAL_NUMBER_KEY: G1_SERIAL_NUMBER}
    response = client.post("/devices/", json=device_payload)
    data = response.json()

    assert response.status_code == 200
    assert data[SERIAL_NUMBER_KEY] == G1_SERIAL_NUMBER


def test_create_read_device_w_attrs(client: TestClient) -> None:
    attrs = [
        {SERIAL_NUMBER_KEY: G1_SERIAL_NUMBER, "key": "string", "value": "kek"},
        {SERIAL_NUMBER_KEY: G1_SERIAL_NUMBER, "key": "float", "value": 1.0},
        {
            SERIAL_NUMBER_KEY: G1_SERIAL_NUMBER,
            "key": "floatarray",
            "value": [1.0, 2.0],
        },
    ]

    device_payload = {
        SERIAL_NUMBER_KEY: G1_SERIAL_NUMBER,
        "attrs": attrs,
    }
    response = client.post("/devices/", json=device_payload)
    assert response.status_code == 200
    response2 = client.get(f"/devices/{G1_SERIAL_NUMBER}")
    data = response2.json()
    for attr in attrs:
        assert attr in data["attributes"]


def test_create_device_with_nonstring_serial_no(client: TestClient) -> None:
    device_payload = {SERIAL_NUMBER_KEY: 1}
    response = client.post(
        "/devices/",
        json=device_payload,
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "Input should be a valid string"
    assert data["detail"][0]["type"] == "string_type"


def test_create_device_with_wrong_format_serial_no(client: TestClient) -> None:
    device_payload = {SERIAL_NUMBER_KEY: "wrong-serial"}
    response = client.post(
        "/devices/",
        json=device_payload,
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"] == "Ill-formatted serial number: wrong-serial"


def test_create_device_with_empty_body(client: TestClient) -> None:
    device_payload: dict[None, None] = {}
    response = client.post(
        "/devices/",
        json=device_payload,
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "Field required"
    assert data["detail"][0]["type"] == "missing"


def test_create_device_with_invalid_device_id(client: TestClient) -> None:
    device_payload = {
        SERIAL_NUMBER_KEY: "00000000-0000-0000-0000-000000000000",
    }
    response = client.post(
        "/devices/",
        json=device_payload,
    )
    data = response.json()

    assert response.status_code == 422
    assert (
        data["detail"]
        == "Ill-formatted serial number: 00000000-0000-0000-0000-000000000000"
    )


def test_create_existing_device(client: TestClient) -> None:
    device_payload = {SERIAL_NUMBER_KEY: G1_SERIAL_NUMBER}
    response = client.post("/devices/", json=device_payload)
    data = response.json()

    assert response.status_code == 200
    assert data[SERIAL_NUMBER_KEY] == G1_SERIAL_NUMBER

    response_2 = client.post("/devices/", json=device_payload)
    data_2 = response_2.json()
    assert response_2.status_code == 409
    assert (
        data_2["detail"]
        == f"A device with serial number {G1_SERIAL_NUMBER} already exists"
    )


def test_get_device(client: TestClient) -> None:
    device_payload = {SERIAL_NUMBER_KEY: G1_SERIAL_NUMBER}
    response = client.post(
        "/devices/",
        json=device_payload,
    )
    data = response.json()

    assert response.status_code == 200
    assert data[SERIAL_NUMBER_KEY] == G1_SERIAL_NUMBER

    device_id = data[SERIAL_NUMBER_KEY]
    response = client.get(f"/devices/{device_id}")
    data = response.json()

    assert response.status_code == 200
    assert data[SERIAL_NUMBER_KEY] == G1_SERIAL_NUMBER


def test_get_device_with_invalid_device_id(client: TestClient) -> None:
    response = client.get("/devices/abc")
    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == "Device not found with serial number: abc"


def test_get_device_with_nonexistent_device_id(client: TestClient) -> None:
    device_id = uuid4()
    response = client.get(f"/devices/{device_id}")
    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == f"Device not found with serial number: {device_id}"


def test_get_all_devices(client: TestClient) -> None:
    device = DeviceCreate.create_mock(serial_number=G1_SERIAL_NUMBER)
    response = client.post(
        "/devices/",
        json=device.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data[SERIAL_NUMBER_KEY] == G1_SERIAL_NUMBER

    device = DeviceCreate.create_mock(serial_number=G2_SERIAL_NUMBER)
    response = client.post(
        "/devices/",
        json=device.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data[SERIAL_NUMBER_KEY] == G2_SERIAL_NUMBER

    response = client.get("/devices/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0][SERIAL_NUMBER_KEY] == G1_SERIAL_NUMBER
    assert data[1][SERIAL_NUMBER_KEY] == G2_SERIAL_NUMBER


def test_get_all_devices_with_limit(client: TestClient) -> None:
    device = DeviceCreate.create_mock(serial_number=G1_SERIAL_NUMBER)
    response = client.post(
        "/devices/",
        json=device.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data[SERIAL_NUMBER_KEY] == G1_SERIAL_NUMBER

    device = DeviceCreate.create_mock(serial_number=G2_SERIAL_NUMBER)
    response = client.post(
        "/devices/",
        json=device.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data[SERIAL_NUMBER_KEY] == G2_SERIAL_NUMBER

    response = client.get("/devices/?limit=1")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0][SERIAL_NUMBER_KEY] == G1_SERIAL_NUMBER


def test_get_all_devices_with_invalid_limit(client: TestClient) -> None:
    response = client.get("/devices/?limit=abc")
    data = response.json()

    assert response.status_code == 422
    assert (
        data["detail"][0]["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )
    assert data["detail"][0]["type"] == "int_parsing"


def test_get_all_devices_with_offset(client: TestClient) -> None:
    device = DeviceCreate.create_mock(serial_number=G1_SERIAL_NUMBER)
    response = client.post(
        "/devices/",
        json=device.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data[SERIAL_NUMBER_KEY] == G1_SERIAL_NUMBER

    device = DeviceCreate.create_mock(serial_number=G2_SERIAL_NUMBER)
    response = client.post(
        "/devices/",
        json=device.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data[SERIAL_NUMBER_KEY] == G2_SERIAL_NUMBER

    response = client.get("/devices/?offset=1")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0][SERIAL_NUMBER_KEY] == G2_SERIAL_NUMBER


def test_get_all_devices_with_invalid_offset(client: TestClient) -> None:
    response = client.get("/devices/?offset=abc")
    data = response.json()

    assert response.status_code == 422
    assert (
        data["detail"][0]["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )
    assert data["detail"][0]["type"] == "int_parsing"


def test_get_all_devices_with_limit_and_offset(client: TestClient) -> None:
    device = DeviceCreate.create_mock(serial_number=G1_SERIAL_NUMBER)
    response = client.post(
        "/devices/",
        json=device.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data[SERIAL_NUMBER_KEY] == G1_SERIAL_NUMBER

    device = DeviceCreate.create_mock(serial_number=G2_SERIAL_NUMBER)
    response = client.post(
        "/devices/",
        json=device.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data[SERIAL_NUMBER_KEY] == G2_SERIAL_NUMBER

    response = client.get("/devices/?limit=1&offset=1")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0][SERIAL_NUMBER_KEY] == G2_SERIAL_NUMBER


def test_get_all_devices_with_invalid_limit_and_offset(client: TestClient) -> None:
    response = client.get("/devices/?limit=abc&offset=abc")
    data = response.json()

    assert response.status_code == 422
    assert (
        data["detail"][0]["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )
    assert data["detail"][0]["type"] == "int_parsing"
    assert (
        data["detail"][1]["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )
    assert data["detail"][1]["type"] == "int_parsing"
