from uuid import uuid4

from fastapi.testclient import TestClient

from api.public.device.models import DeviceCreate
from api.public.pulse.models import PulseCreate


def test_create_pulse(client: TestClient) -> None:
    """Test creating a pulse.

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
    device_data = response.json()
    pulse = PulseCreate.create_mock(
        device_id=device_data["device_id"],
        length=100,
        timescale=1e-9,
        amplitude=50.0,
    )
    response = client.post(
        "/pulses/",
        json=pulse.as_dict(),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["device_id"] == data["device_id"]
    assert data["delays"] == pulse.delays
    assert data["signal"] == pulse.signal
    assert data["integration_time"] == pulse.integration_time
    assert data["creation_time"] is not None
    assert data["pulse_id"] is not None


def test_create_pulse_with_invalid_delays(client: TestClient) -> None:
    """Test creating a pulse with invalid delays.

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
    device_data = response.json()
    pulse = PulseCreate.create_mock(
        device_id=device_data["device_id"],
        length=100,
        timescale=1e-9,
        amplitude=50.0,
    )
    response = client.post(
        "/pulses/",
        json={**pulse.as_dict(), "delays": [1, "a"]},
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid float"
    assert data["detail"][0]["type"] == "type_error.float"


def test_create_pulse_with_invalid_signal(client: TestClient) -> None:
    """Test creating a pulse with invalid signal.

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
    device_data = response.json()
    pulse = PulseCreate.create_mock(
        device_id=device_data["device_id"],
        length=100,
        timescale=1e-9,
        amplitude=50.0,
    )
    response = client.post(
        "/pulses/",
        json={**pulse.as_dict(), "signal": [1, "a"]},
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid float"
    assert data["detail"][0]["type"] == "type_error.float"


def test_create_pulse_with_invalid_integration_time(client: TestClient) -> None:
    """Test creating a pulse with invalid integration time.

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
    device_data = response.json()

    pulse = PulseCreate.create_mock(
        device_id=device_data["device_id"],
        length=100,
        timescale=1e-9,
        amplitude=50.0,
    )
    response = client.post(
        "/pulses/",
        json={**pulse.as_dict(), "integration_time": "a"},
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid integer"
    assert data["detail"][0]["type"] == "type_error.integer"


def test_create_pulse_with_invalid_device_id(client: TestClient) -> None:
    """Test creating a pulse with invalid device id.

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
    device_data = response.json()

    pulse = PulseCreate.create_mock(
        device_id=device_data["device_id"],
        length=100,
        timescale=1e-9,
        amplitude=50.0,
    )
    response = client.post(
        "/pulses/",
        json={**pulse.as_dict(), "device_id": "a"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "value is not a valid uuid"
    assert response.json()["detail"][0]["type"] == "type_error.uuid"


def test_get_pulse(client: TestClient) -> None:
    """Test getting a pulse.

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
    device_data = response.json()
    pulse = PulseCreate.create_mock(
        device_id=device_data["device_id"],
        length=100,
        timescale=1e-9,
        amplitude=50.0,
    )
    response = client.post(
        "/pulses/",
        json=pulse.as_dict(),
    )
    pulse_data = response.json()
    response = client.get(f"/pulses/{pulse_data['pulse_id']}")
    data = response.json()

    assert response.status_code == 200
    assert data["device_id"] == pulse_data["device_id"]
    assert data["delays"] == pulse.delays
    assert data["signal"] == pulse.signal
    assert data["integration_time"] == pulse.integration_time
    assert data["creation_time"] == pulse_data["creation_time"]
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


def test_get_all_pulses(client: TestClient) -> None:
    """Test getting all pulses.

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
    device_data = response.json()
    pulse = PulseCreate.create_mock(
        device_id=device_data["device_id"],
        length=100,
        timescale=1e-9,
        amplitude=50.0,
    )
    response = client.post(
        "/pulses/",
        json=pulse.as_dict(),
    )
    pulse_data = response.json()
    response = client.get("/pulses/")
    data = response.json()

    assert response.status_code == 200
    assert data[0]["device_id"] == pulse_data["device_id"]
    assert data[0]["delays"] == pulse.delays
    assert data[0]["signal"] == pulse.signal
    assert data[0]["integration_time"] == pulse.integration_time
    assert data[0]["creation_time"] == pulse_data["creation_time"]
    assert data[0]["pulse_id"] == pulse_data["pulse_id"]
