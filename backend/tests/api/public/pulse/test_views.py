from uuid import uuid4

from fastapi.testclient import TestClient


def test_create_pulse(client: TestClient, device_uuid: str) -> None:
    """Test creating a pulse.

    Args:
    ----
        client (TestClient): The test client.
        device_uuid (str): The uuid of the device.

    Returns:
    -------
        None
    """
    pulse_payload = {
        "device_id": device_uuid,
        "delays": [1, 2, 3],
        "signal": [1, 2, 3],
        "integration_time": 100,
        "creation_time": "2021-01-01T00:00:00",
    }
    response = client.post(
        "/pulses/",
        json=pulse_payload,
    )
    data = response.json()

    assert response.status_code == 200
    assert data["device_id"] == device_uuid
    assert data["delays"] == [1, 2, 3]
    assert data["signal"] == [1, 2, 3]
    assert data["integration_time"] == 100
    assert data["creation_time"] == "2021-01-01T00:00:00"
    assert data["pulse_id"] is not None


def test_create_pulse_with_invalid_delays(client: TestClient, device_uuid: str) -> None:
    """Test creating a pulse with invalid delays.

    Args:
    ----
        client (TestClient): The test client.
        device_uuid (str): The uuid of the device.

    Returns:
    -------
        None
    """
    pulse_payload = {
        "device_id": device_uuid,
        "delays": [1, "a"],
        "signal": [1, 2, 3],
        "integration_time": 100,
        "creation_time": "2021-01-01T00:00:00",
    }
    response = client.post(
        "/pulses/",
        json=pulse_payload,
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid float"
    assert data["detail"][0]["type"] == "type_error.float"


def test_create_pulse_with_invalid_signal(client: TestClient, device_uuid: str) -> None:
    """Test creating a pulse with invalid signal.

    Args:
    ----
        client (TestClient): The test client.
        device_uuid (str): The uuid of the device.

    Returns:
    -------
        None
    """
    pulse_payload = {
        "device_id": device_uuid,
        "delays": [1, 2, 3],
        "signal": [1, "a"],
        "integration_time": 100,
        "creation_time": "2021-01-01T00:00:00",
    }
    response = client.post(
        "/pulses/",
        json=pulse_payload,
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid float"
    assert data["detail"][0]["type"] == "type_error.float"


def test_create_pulse_with_invalid_integration_time(
    client: TestClient,
    device_uuid: str,
) -> None:
    """Test creating a pulse with invalid integration time.

    Args:
    ----
        client (TestClient): The test client.
        device_uuid (str): The uuid of the device.

    Returns:
    -------
        None
    """
    pulse_payload = {
        "device_id": device_uuid,
        "delays": [1, 2, 3],
        "signal": [1, 2, 3],
        "integration_time": "a",
        "creation_time": "2021-01-01T00:00:00",
    }

    response = client.post(
        "/pulses/",
        json=pulse_payload,
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid integer"
    assert data["detail"][0]["type"] == "type_error.integer"


def test_create_pulse_with_nonexistent_device_id(
    client: TestClient,
) -> None:
    """Test creating a pulse with nonexistent device id.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    pulse_payload = {
        "device_id": str(uuid4()),
        "delays": [1, 2, 3],
        "signal": [1, 2, 3],
        "integration_time": 100,
        "creation_time": "2021-01-01T00:00:00",
    }
    response = client.post(
        "/pulses/",
        json=pulse_payload,
    )

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == f"Device not found with id: {pulse_payload['device_id']}"
    )


def test_create_pulse_with_invalid_device_id(
    client: TestClient,
    device_uuid: str,
) -> None:
    """Test creating a pulse with invalid device id.

    Args:
    ----
        client (TestClient): The test client.
        device_uuid (str): The uuid of the device.

    Returns:
    -------
        None
    """
    pulse_payload = {
        "device_id": "a",
        "delays": [1, 2, 3],
        "signal": [1, 2, 3],
        "integration_time": 100,
        "creation_time": "2021-01-01T00:00:00",
    }
    response = client.post(
        "/pulses/",
        json=pulse_payload,
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "value is not a valid uuid"
    assert response.json()["detail"][0]["type"] == "type_error.uuid"


def test_create_pulse_with_invalid_creation_time(
    client: TestClient,
    device_uuid: str,
) -> None:
    """Test creating a pulse with invalid creation time.

    Args:
    ----
        client (TestClient): The test client.
        device_uuid (str): The uuid of the device.

    Returns:
    -------
        None
    """
    pulse_payload = {
        "device_id": device_uuid,
        "delays": [1, 2, 3],
        "signal": [1, 2, 3],
        "integration_time": 100,
        "creation_time": "a",
    }
    response = client.post(
        "/pulses/",
        json=pulse_payload,
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "invalid datetime format"
    assert response.json()["detail"][0]["type"] == "value_error.datetime"


def test_get_pulse(client: TestClient, device_uuid: str) -> None:
    """Test getting a pulse.

    Args:
    ----
        client (TestClient): The test client.
        device_uuid (str): The uuid of the device.

    Returns:
    -------
        None
    """
    pulse_payload = {
        "device_id": device_uuid,
        "delays": [1, 2, 3],
        "signal": [1, 2, 3],
        "integration_time": 100,
        "creation_time": "2021-01-01T00:00:00",
    }
    response = client.post(
        "/pulses/",
        json=pulse_payload,
    )

    pulse_data = response.json()

    response = client.get(f"/pulses/{pulse_data['pulse_id']}")
    data = response.json()

    assert response.status_code == 200
    assert data["device_id"] == device_uuid
    assert data["delays"] == [1, 2, 3]
    assert data["signal"] == [1, 2, 3]
    assert data["integration_time"] == 100
    assert data["creation_time"] == "2021-01-01T00:00:00"
    assert data["pulse_id"] == pulse_data["pulse_id"]


def test_get_pulse_with_invalid_pulse_id(client: TestClient) -> None:
    """Test getting a pulse with an invalid pulse id.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    response = client.get("/pulses/abc")
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid uuid"
    assert data["detail"][0]["type"] == "type_error.uuid"


def test_get_pulse_with_nonexistent_pulse_id(client: TestClient) -> None:
    """Test getting a pulse with a nonexistent pulse id.

    Args:
    ----
        client (TestClient): The test client.

    Returns:
    -------
        None
    """
    pulse_id = uuid4()
    response = client.get(f"/pulses/{pulse_id}")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == f"Pulse not found with id: {pulse_id}"


def test_get_all_pulses(client: TestClient, device_uuid: str) -> None:
    """Test getting all pulses.

    Args:
    ----
        client (TestClient): The test client.
        device_uuid (str): The uuid of the device.

    Returns:
    -------
        None
    """
    pulse_1_payload = {
        "device_id": device_uuid,
        "delays": [1, 2, 3],
        "signal": [1, 2, 3],
        "integration_time": 100,
        "creation_time": "2021-01-01T00:00:00",
    }
    pulse_1_response = client.post(
        "/pulses/",
        json=pulse_1_payload,
    )
    pulse_1_data = pulse_1_response.json()

    pulse_2_payload = {
        "device_id": device_uuid,
        "delays": [4, 5, 6],
        "signal": [4, 5, 6],
        "integration_time": 200,
        "creation_time": "2021-02-01T00:00:00",
    }
    pulse_2_response = client.post(
        "/pulses/",
        json=pulse_2_payload,
    )
    pulse_2_data = pulse_2_response.json()

    response = client.get("/pulses/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["device_id"] == device_uuid
    assert data[0]["delays"] == [1, 2, 3]
    assert data[0]["signal"] == [1, 2, 3]
    assert data[0]["integration_time"] == 100
    assert data[0]["creation_time"] == "2021-01-01T00:00:00"
    assert data[0]["pulse_id"] == pulse_1_data["pulse_id"]
    assert data[1]["device_id"] == device_uuid
    assert data[1]["delays"] == [4, 5, 6]
    assert data[1]["signal"] == [4, 5, 6]
    assert data[1]["integration_time"] == 200
    assert data[1]["creation_time"] == "2021-02-01T00:00:00"
    assert data[1]["pulse_id"] == pulse_2_data["pulse_id"]