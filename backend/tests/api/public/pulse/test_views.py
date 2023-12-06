from datetime import datetime
from typing import Any
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from api.public.attrs.models import PulseAttrsFloatCreate, PulseAttrsStrCreate
from api.public.pulse.models import PulseCreate, TPulseDict
from api.utils.mock_data_generator import create_devices_and_pulses


def test_create_pulse(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    response = client.get(f"/pulses/{pulse_id}")

    response_data = response.json()

    assert response.status_code == 200
    _assert_equal_pulses(response_data, pulse_payload[0])
    assert response_data["pulse_id"] == pulse_id


def test_create_pulse_w_errors(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock_w_errs(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    response = client.get(f"/pulses/{pulse_id}")

    response_data = response.json()

    assert response.status_code == 200
    _assert_equal_pulses(response_data, pulse_payload[0])
    assert response_data["pulse_id"] == pulse_id


def test_create_pulse_with_invalid_json(client: TestClient, device_id: UUID) -> None:
    pulse_payload = PulseCreate.create_mock(device_id=device_id).as_dict()

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    assert pulse_response.status_code == 422


def test_create_pulse_with_invalid_delays(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]
    pulse_payload[0]["delays"] = [1, "a", 3]  # type: ignore[list-item]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()

    assert pulse_response.status_code == 422
    assert (
        pulse_data["detail"][0]["msg"]
        == "Input should be a valid number, unable to parse string as a number"
    )
    assert pulse_data["detail"][0]["type"] == "float_parsing"


def test_create_pulse_with_invalid_signal(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]
    pulse_payload[0]["signal"] = [1, "a", 3]  # type: ignore[list-item]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()

    assert pulse_response.status_code == 422
    assert (
        pulse_data["detail"][0]["msg"]
        == "Input should be a valid number, unable to parse string as a number"
    )
    assert pulse_data["detail"][0]["type"] == "float_parsing"


def test_create_pulse_with_invalid_integration_time(
    client: TestClient,
    device_id: UUID,
) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]
    pulse_payload[0]["integration_time_ms"] = "a"  # type: ignore[typeddict-item]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()

    assert pulse_response.status_code == 422
    assert (
        pulse_data["detail"][0]["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )
    assert pulse_data["detail"][0]["type"] == "int_parsing"


def test_create_pulse_with_nonexistent_device_id(client: TestClient) -> None:
    device_id = uuid4()
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    assert pulse_response.status_code == 404
    assert pulse_response.json()["detail"] == f"Device not found with id: {device_id}"


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
    assert pulse_response.json()["detail"][0]["msg"] == (
        "Input should be a valid UUID, invalid length: "
        "expected length 32 for simple format, found 1"
    )
    assert pulse_response.json()["detail"][0]["type"] == "uuid_parsing"


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
    assert (
        pulse_response.json()["detail"][0]["msg"]
        == "Input should be a valid datetime, input is too short"
    )
    assert pulse_response.json()["detail"][0]["type"] == "datetime_parsing"


def test_get_pulse_with_invalid_pulse_id(client: TestClient) -> None:
    response = client.get("/pulses/abc")
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == (
        "Input should be a valid UUID, invalid length: "
        "expected length 32 for simple format, found 3"
    )
    assert data["detail"][0]["type"] == "uuid_parsing"


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

    pulses_response = client.post(
        "/pulses/create/",
        json=pulses_payload,
    )

    pulse_ids = pulses_response.json()

    response = client.get("/pulses/")

    pulses_data = response.json()

    assert pulses_response.status_code == 200
    assert len(pulses_data) == 2
    _assert_equal_pulses(pulses_data[0], pulses_payload[0])
    _assert_equal_pulses(pulses_data[1], pulses_payload[1])
    assert pulses_data[0]["pulse_id"] == pulse_ids[0]
    assert pulses_data[1]["pulse_id"] == pulse_ids[1]


def test_read_pulses_with_ids(client: TestClient) -> None:
    create_devices_and_pulses()
    all_pulses = client.get("/pulses/").json()
    wanted_pulse_ids = [pulse["pulse_id"] for pulse in all_pulses][:-1]
    selected_pulses = client.post("/pulses/get", json=wanted_pulse_ids).json()
    selected_pulse_ids = [pulse["pulse_id"] for pulse in selected_pulses]
    assert wanted_pulse_ids == selected_pulse_ids
    assert {"key": "angle", "value": 29.0} in selected_pulses[0]["pulse_attributes"]
    assert {"key": "angle", "value": 17.1} in selected_pulses[0]["pulse_attributes"]
    assert {"key": "substrate", "value": "sand-blasted steel"} in selected_pulses[0][
        "pulse_attributes"
    ]


def test_read_pulses_with_error(client: TestClient, device_id: UUID) -> None:
    pulses_payload = [
        PulseCreate.create_mock_w_errs(device_id=device_id, length=2).as_dict()
        for _ in range(1)
    ]

    pulses_response = client.post(
        "/pulses/create/",
        json=pulses_payload,
    ).json()

    selected_pulses = client.post("/pulses/get", json=[pulses_response[0]]).json()
    assert selected_pulses[0]["signal_error"] == pulses_payload[0]["signal_error"]


def test_read_pulses_with_nonexisting_id(client: TestClient) -> None:
    create_devices_and_pulses()
    nonexistent_id = str(uuid4())
    response = client.post("/pulses/get", json=[nonexistent_id])

    assert response.status_code == 404
    assert nonexistent_id in response.json()["detail"]


def test_create_pulse_with_attrs(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_str_attr_payload = PulseAttrsStrCreate.create_mock().as_dict()
    pulse_float_attr_payload = PulseAttrsFloatCreate.create_mock().as_dict()
    pulse_int_attr_payload = PulseAttrsFloatCreate.create_mock(value=42).as_dict()

    pulse_payload[0]["pulse_attributes"] = [
        pulse_str_attr_payload,
        pulse_float_attr_payload,
        pulse_int_attr_payload,
    ]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    response = client.get(f"/pulses/{pulse_id}")
    response_attrs = client.get(f"/pulses/{pulse_id}/attrs")

    response_data = response.json()
    response_attrs_data = response_attrs.json()

    expected_str_attr = {**pulse_str_attr_payload}
    expected_str_attr.pop("data_type")
    expected_float_attr = {**pulse_float_attr_payload}
    expected_float_attr.pop("data_type")
    expected_int_attr = {**pulse_int_attr_payload}
    expected_int_attr.pop("data_type")

    assert response.status_code == 200
    assert response_attrs.status_code == 200
    _assert_equal_pulses(response_data, pulse_payload[0])
    assert response_data["pulse_id"] == pulse_id
    assert expected_str_attr in response_attrs_data[pulse_id]
    assert expected_float_attr in response_attrs_data[pulse_id]
    assert expected_int_attr in response_attrs_data[pulse_id]


def test_add_pulses_raises_err_on_wrong_datatype(
    client: TestClient,
    device_id: UUID,
) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]
    pulse_float_attr_payload = PulseAttrsFloatCreate.create_mock().as_dict()

    pulse_payload[0]["pulse_attributes"] = [pulse_float_attr_payload]
    created_pulses_ids = client.post(
        "/pulses/create/",
        json=pulse_payload,
    ).json()

    # Now add a new pulse with the same key, but a different datatype
    new_pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]
    new_pulse_attr_payload = {**pulse_float_attr_payload}
    new_pulse_attr_payload["data_type"] = "string"
    new_pulse_payload[0]["pulse_attributes"] = [new_pulse_attr_payload]  # type: ignore[list-item]

    wrong_pulse_response = client.post(
        "/pulses/create/",
        json=new_pulse_payload,
    )

    # Check that the response is a 400 error due to the wrong datatype
    assert wrong_pulse_response.status_code == 400
    assert (
        "Key mock_float_key already exists with data type"
        in wrong_pulse_response.json()["detail"]
    )

    # Check that no additional pulses were added to the database
    all_pulses = client.get("/pulses").json()
    assert len(all_pulses) == 1
    assert created_pulses_ids[0] == all_pulses[0]["pulse_id"]


def test_add_pulses_saves_new_keys(
    client: TestClient,
    device_id: UUID,
) -> None:
    keys = client.get("/attrs/keys").json()
    assert len(keys) == 0
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]
    pulse_float_attr_payload = PulseAttrsFloatCreate.create_mock().as_dict()
    pulse_payload[0]["pulse_attributes"] = [pulse_float_attr_payload]
    client.post(
        "/pulses/create/",
        json=pulse_payload,
    )
    new_keys = client.get("/attrs/keys").json()
    assert len(new_keys) == 1


def _assert_equal_pulses(
    received_pulse: dict[str, Any],
    created_pulse: TPulseDict,
) -> None:
    """Assert that two pulses are equal."""
    # The creation_time is stored as UTC in the database.
    # We thus need to read in the ISO time, convert to UTC, and back to a string,
    # so we can compare with what comes out of the database.
    creation_time = (
        datetime.fromisoformat(
            created_pulse["creation_time"],
        )
        .astimezone(ZoneInfo("UTC"))
        .strftime("%Y-%m-%dT%H:%M:%S.%f")
    )
    assert received_pulse["device_id"] == created_pulse["device_id"]
    assert received_pulse["delays"] == created_pulse["delays"]
    assert received_pulse["signal"] == created_pulse["signal"]
    assert received_pulse["integration_time_ms"] == created_pulse["integration_time_ms"]
    assert received_pulse["creation_time"] == creation_time
