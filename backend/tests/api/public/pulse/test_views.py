from datetime import datetime
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from api.public.pulse.models import PulseCreate
from api.utils.mock_data_generator import create_devices_and_pulses


def test_create_pulse(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    # The creation_time is stored as UTC in the database.
    # We thus need to read in the ISO time, convert to UTC, and back to a string,
    # so we can compare with what comes out of the database.
    pulse_create_datetime = (
        datetime.fromisoformat(
            pulse_payload[0]["creation_time"],
        )
        .astimezone(ZoneInfo("UTC"))
        .strftime("%Y-%m-%dT%H:%M:%S.%f")
    )

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    response = client.get(f"/pulses/{pulse_id}")

    response_data = response.json()

    assert response.status_code == 200
    assert response_data["device_id"] == device_id
    assert response_data["delays"] == pulse_payload[0]["delays"]
    assert response_data["signal"] == pulse_payload[0]["signal"]
    assert response_data["integration_time"] == pulse_payload[0]["integration_time"]
    assert response_data["creation_time"] == pulse_create_datetime
    assert response_data["pulse_id"] == pulse_id


def test_create_pulse_with_invalid_delays(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]
    pulse_payload[0]["delays"] = [1, "a", 3]  # type: ignore[list-item]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()

    assert pulse_response.status_code == 422
    assert pulse_data["detail"][0]["msg"] == "value is not a valid float"
    assert pulse_data["detail"][0]["type"] == "type_error.float"


def test_create_pulse_with_invalid_signal(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]
    pulse_payload[0]["signal"] = [1, "a", 3]  # type: ignore[list-item]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()

    assert pulse_response.status_code == 422
    assert pulse_data["detail"][0]["msg"] == "value is not a valid float"
    assert pulse_data["detail"][0]["type"] == "type_error.float"


def test_create_pulse_with_invalid_integration_time(
    client: TestClient,
    device_id: UUID,
) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]
    pulse_payload[0]["integration_time"] = "a"  # type: ignore[typeddict-item]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()

    assert pulse_response.status_code == 422
    assert pulse_data["detail"][0]["msg"] == "value is not a valid integer"
    assert pulse_data["detail"][0]["type"] == "type_error.integer"


def test_create_pulse_with_nonexistent_device_id(
    client: TestClient,
    device_id: UUID,
) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=uuid4()).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    assert pulse_response.status_code == 404
    assert pulse_response.json()["detail"] == "Device not found with id: 1000"


def test_create_pulse_with_invalid_device_id(
    client: TestClient,
    device_id: UUID,
) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]
    pulse_payload[0]["device_id"] = "a"

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    assert pulse_response.status_code == 422
    assert pulse_response.json()["detail"][0]["msg"] == "value is not a valid uuid"
    assert pulse_response.json()["detail"][0]["type"] == "type_error.uuid"


def test_create_pulse_with_invalid_creation_time(
    client: TestClient,
    device_id: UUID,
) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]
    pulse_payload[0]["creation_time"] = "a"

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    assert pulse_response.status_code == 422
    assert pulse_response.json()["detail"][0]["msg"] == "invalid datetime format"
    assert pulse_response.json()["detail"][0]["type"] == "value_error.datetime"


def test_get_pulse_with_invalid_pulse_id(client: TestClient) -> None:
    response = client.get("/pulses/abc")
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "value is not a valid uuid"
    assert data["detail"][0]["type"] == "type_error.uuid"


def test_get_pulse_with_nonexistent_pulse_id(client: TestClient) -> None:
    pulse_id = uuid4()
    response = client.get(f"/pulses/{pulse_id}")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == f"Pulse not found with id: {pulse_id}"


def test_get_all_pulses(client: TestClient, device_id: UUID) -> None:
    pulses_payload = [
        PulseCreate.create_mock(device_id=device_id).as_dict() for _ in range(2)
    ]

    pulse_1_creation_time = (
        datetime.fromisoformat(
            pulses_payload[0]["creation_time"],
        )
        .astimezone(ZoneInfo("UTC"))
        .strftime("%Y-%m-%dT%H:%M:%S.%f")
    )
    pulse_2_creation_time = (
        datetime.fromisoformat(
            pulses_payload[1]["creation_time"],
        )
        .astimezone(ZoneInfo("UTC"))
        .strftime("%Y-%m-%dT%H:%M:%S.%f")
    )

    pulses_response = client.post(
        "/pulses/create/",
        json=pulses_payload,
    )

    pulse_ids = pulses_response.json()

    response = client.get("/pulses/")

    pulses_data = response.json()

    assert pulses_response.status_code == 200
    assert len(pulses_data) == 2
    assert pulses_data[0]["device_id"] == device_id
    assert pulses_data[0]["delays"] == pulses_payload[0]["delays"]
    assert pulses_data[0]["signal"] == pulses_payload[0]["signal"]
    assert pulses_data[0]["integration_time"] == pulses_payload[0]["integration_time"]
    assert pulses_data[0]["creation_time"] == pulse_1_creation_time
    assert pulses_data[0]["pulse_id"] == pulse_ids[0]
    assert pulses_data[1]["device_id"] == device_id
    assert pulses_data[1]["delays"] == pulses_payload[1]["delays"]
    assert pulses_data[1]["signal"] == pulses_payload[1]["signal"]
    assert pulses_data[1]["integration_time"] == pulses_payload[1]["integration_time"]
    assert pulses_data[1]["creation_time"] == pulse_2_creation_time
    assert pulses_data[1]["pulse_id"] == pulse_ids[1]


def test_read_pulses_with_ids(client: TestClient) -> None:
    create_devices_and_pulses()
    all_pulses = client.get("/pulses/").json()
    wanted_pulse_ids = [pulse["pulse_id"] for pulse in all_pulses][:-1]
    selected_pulses = client.post("/pulses/get", json=wanted_pulse_ids).json()
    selected_pulse_ids = [pulse["pulse_id"] for pulse in selected_pulses]
    assert wanted_pulse_ids == selected_pulse_ids
