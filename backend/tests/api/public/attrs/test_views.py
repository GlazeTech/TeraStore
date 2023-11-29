from datetime import datetime, timedelta
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.public.attrs.models import (
    AttrDataType,
    PulseAttrsFloatCreate,
    PulseAttrsStrCreate,
)
from api.public.pulse.models import PulseCreate
from api.utils.helpers import get_now
from api.utils.mock_data_generator import create_devices_and_pulses


def test_get_all_keys(client: TestClient) -> None:
    create_devices_and_pulses()

    response = client.get("/attrs/keys/")

    response_data = response.json()

    assert response.status_code == 200
    assert {"data_type": "float", "name": "angle"} in response_data
    assert {"data_type": "string", "name": "substrate"} in response_data


def test_get_all_values_on_key(client: TestClient) -> None:
    create_devices_and_pulses()

    response = client.get("/attrs/angle/values/")

    response_data = response.json()

    assert response.status_code == 200
    assert response_data == [17.1, 23.2, 24.5, 29.0]


def test_get_all_values_on_non_existing_key(client: TestClient) -> None:
    create_devices_and_pulses()

    response = client.get("/attrs/non-existing-key/values/")

    response_data = response.json()

    assert response.status_code == 404
    assert response_data["detail"] == "Key non-existing-key does not exist."


def test_get_attrs_on_pulse(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    attrs_1_payload = PulseAttrsStrCreate.create_mock().as_dict()

    attrs_1_data = client.put(
        f"/pulses/{pulse_id}/attrs/",
        json=attrs_1_payload,
    )

    attrs_2_payload = PulseAttrsFloatCreate.create_mock().as_dict()

    attrs_2_data = client.put(
        f"/pulses/{pulse_id}/attrs/",
        json=attrs_2_payload,
    )

    response = client.get(f"/pulses/{pulse_id}/attrs/")
    response_data = response.json()

    response_keys = [d["key"] for d in response_data]
    response_values = [d["value"] for d in response_data]

    assert pulse_response.status_code == 200
    assert attrs_1_data.status_code == 200
    assert attrs_2_data.status_code == 200
    assert response.status_code == 200
    assert len(response_data) == 2
    assert attrs_1_payload["key"] in response_keys
    assert attrs_2_payload["key"] in response_keys
    assert attrs_1_payload["value"] in response_values
    assert attrs_2_payload["value"] in response_values


def test_get_pulse_attrs_on_non_existing_pulse(client: TestClient) -> None:
    pulse_id = uuid4()

    response = client.get(f"/pulses/{pulse_id}/attrs/")

    response_data = response.json()

    assert response.status_code == 404
    assert response_data["detail"] == f"Pulse not found with id: {pulse_id}"


def test_add_pulse_attrs_on_pulse(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    attrs_payload = PulseAttrsStrCreate.create_mock().as_dict()

    attrs_response = client.put(
        f"/pulses/{pulse_id}/attrs/",
        json=attrs_payload,
    )

    response = client.get(f"/pulses/{pulse_id}/attrs/")
    response_data = response.json()

    response_keys = [d["key"] for d in response_data]
    response_values = [d["value"] for d in response_data]

    assert pulse_response.status_code == 200
    assert attrs_response.status_code == 200
    assert response.status_code == 200
    assert len(response_data) == 1
    assert attrs_payload["key"] in response_keys
    assert attrs_payload["value"] in response_values


def test_add_pulse_attrs_on_non_existing_pulse(client: TestClient) -> None:
    pulse_id = uuid4()

    attrs_payload = PulseAttrsStrCreate.create_mock().as_dict()

    response = client.put(
        f"/pulses/{pulse_id}/attrs/",
        json=attrs_payload,
    )

    response_data = response.json()

    assert response.status_code == 404
    assert response_data["detail"] == f"Pulse not found with id: {pulse_id}"


def test_add_existing_attr_wrong_type(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    attrs_payload = PulseAttrsStrCreate.create_mock().as_dict()

    attrs_1_response = client.put(
        f"/pulses/{pulse_id}/attrs/",
        json=attrs_payload,
    )

    attrs_payload["data_type"] = AttrDataType.FLOAT

    attrs_2_response = client.put(
        f"/pulses/{pulse_id}/attrs/",
        json=attrs_payload,
    )

    attrs_2_response_data = attrs_2_response.json()

    assert pulse_response.status_code == 200
    assert attrs_1_response.status_code == 200
    assert attrs_2_response.status_code == 400
    assert attrs_2_response_data["detail"] == (
        f"Key {attrs_payload['key']} already exists with data type 'string'. "
        f"You gave 'float'."
    )


def test_filtering_pulses_float(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    pulse_attrs_payload = PulseAttrsFloatCreate.create_mock(value=42.0).as_dict()

    pulse_attrs_data = client.put(
        f"/pulses/{pulse_id}/attrs/",
        json=pulse_attrs_payload,
    )

    filtering_json = {
        "kv_pairs": [
            {
                "key": "mock_float_key",
                "min_value": 42.0,
                "max_value": 42.0,
            },
        ],
        "columns": ["pulse_id"],
    }

    response = client.post("/attrs/filter/", json=filtering_json)
    response_data = response.json()

    assert pulse_response.status_code == 200
    assert pulse_attrs_data.status_code == 200
    assert response.status_code == 200
    assert len(response_data) == 1
    assert pulse_id in response_data[0]


def test_filtering_pulses_string(
    client: TestClient,
    device_id: UUID,
) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    pulse_attrs_payload = PulseAttrsStrCreate.create_mock().as_dict()

    pulse_attrs_data = client.put(
        f"/pulses/{pulse_id}/attrs/",
        json=pulse_attrs_payload,
    )

    filtering_json = {
        "kv_pairs": [
            {
                "key": "mock_string_key",
                "value": "mock_string_value",
            },
        ],
        "columns": ["pulse_id"],
    }

    response = client.post("/attrs/filter/", json=filtering_json)
    response_data = response.json()

    assert pulse_response.status_code == 200
    assert pulse_attrs_data.status_code == 200
    assert response.status_code == 200
    assert len(response_data) == 1
    assert pulse_id in response_data[0]


def test_filter_all_datatypes(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    pulse_attrs_1_payload = PulseAttrsStrCreate.create_mock().as_dict()

    pulse_1_attrs_response = client.put(
        f"/pulses/{pulse_id}/attrs/",
        json=pulse_attrs_1_payload,
    )

    pulse_attrs_2_payload = PulseAttrsFloatCreate.create_mock().as_dict()

    pulse_2_attrs_response = client.put(
        f"/pulses/{pulse_id}/attrs/",
        json=pulse_attrs_2_payload,
    )

    filtering_json = {
        "kv_pairs": [
            {
                "key": "mock_float_key",
                "min_value": 42.0,
                "max_value": 42.0,
            },
            {
                "key": "mock_string_key",
                "value": "mock_string_value",
            },
        ],
        "columns": ["pulse_id"],
    }

    response = client.post("/attrs/filter/", json=filtering_json)

    response_data = response.json()

    assert pulse_response.status_code == 200
    assert pulse_1_attrs_response.status_code == 200
    assert pulse_2_attrs_response.status_code == 200
    assert response.status_code == 200
    assert len(response_data) == 1
    assert pulse_id in response_data[0]


def test_filter_no_kv_given(client: TestClient, device_id: str) -> None:
    filtering_json = {
        "kv_pairs": [],
        "columns": ["pulse_id"],
    }

    response = client.post("/attrs/filter/", json=filtering_json)

    response_data = response.json()

    assert response.status_code == 200
    assert response_data == []


def test_filter_no_kv_one_pulse(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )
    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]
    filtering_json = {
        "kv_pairs": [],
        "columns": ["pulse_id"],
    }

    response = client.post("/attrs/filter/", json=filtering_json)

    response_data = response.json()

    assert response.status_code == 200
    assert response_data == [[pulse_id]]


def test_filter_non_existent_key(client: TestClient, device_id: str) -> None:
    filtering_json = {
        "kv_pairs": [
            {
                "key": "non-existent-key",
                "value": "test",
            },
        ],
        "columns": ["pulse_id"],
    }

    response = client.post("/attrs/filter/", json=filtering_json)

    response_data = response.json()

    assert response.status_code == 404
    assert response_data["detail"] == "Key non-existent-key does not exist."


def test_filter_one_wrong(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    pulse_attrs_1_payload = PulseAttrsStrCreate.create_mock().as_dict()

    pulse_1_attrs_response = client.put(
        f"/pulses/{pulse_id}/attrs/",
        json=pulse_attrs_1_payload,
    )

    pulse_attrs_2_payload = PulseAttrsFloatCreate.create_mock().as_dict()

    pulse_2_attrs_response = client.put(
        f"/pulses/{pulse_id}/attrs/",
        json=pulse_attrs_2_payload,
    )

    filtering_json = {
        "kv_pairs": [
            {
                # Value is incorrect, so zero results should be returned.
                "key": "mock_float_key",
                "min_value": 40.0,
                "max_value": 41.0,
            },
            {
                "key": "mock_string_key",
                "value": "mock_string_value",
            },
        ],
        "columns": ["pulse_id"],
    }

    response = client.post("/attrs/filter/", json=filtering_json)

    response_data = response.json()

    assert pulse_response.status_code == 200
    assert pulse_1_attrs_response.status_code == 200
    assert pulse_2_attrs_response.status_code == 200
    assert response.status_code == 200
    assert len(response_data) == 0


def test_filter_valid_creation_time(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    today = get_now()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    filtering_json = {
        "kv_pairs": [
            {
                "key": "creation_time",
                "min_value": yesterday.isoformat(),
                "max_value": tomorrow.isoformat(),
            },
        ],
        "columns": ["pulse_id"],
    }

    response = client.post("/attrs/filter/", json=filtering_json)
    response_data = response.json()

    assert pulse_response.status_code == 200
    assert response.status_code == 200
    assert len(response_data) == 1
    assert pulse_id in response_data[0]


def test_filter_invalid_creation_time(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    filtering_json = {
        "kv_pairs": [
            {
                "key": "creation_time",
                "min_value": "invalid",
                "max_value": "invalid",
            },
        ],
        "columns": ["pulse_id"],
    }

    response = client.post("/attrs/filter/", json=filtering_json)

    assert pulse_response.status_code == 200
    assert response.status_code == 422


def test_filter_valid_creation_time_no_hits(
    client: TestClient,
    device_id: UUID,
) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]

    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )

    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    today = get_now()
    tomorrow = today + timedelta(days=1)

    filtering_json = {
        "kv_pairs": [
            {
                "key": "creation_time",
                "min_value": tomorrow.isoformat(),
                "max_value": tomorrow.isoformat(),
            },
        ],
        "columns": ["pulse_id"],
    }

    response = client.post("/attrs/filter/", json=filtering_json)
    response_data = response.json()

    assert pulse_response.status_code == 200
    assert response.status_code == 200
    assert len(response_data) == 0
    assert pulse_id not in response_data


def test_filter_wrong_column_name(client: TestClient, device_id: int) -> None:
    filtering_json = {
        "kv_pairs": [],
        "columns": ["nonexistent_column"],
    }

    response = client.post("/attrs/filter/", json=filtering_json)
    response_data = response.json()

    assert response.status_code == 404
    assert "Pulse column not found" in response_data["detail"]


def test_filter_valid_creation_time_multiple_columns(
    client: TestClient,
    device_id: UUID,
) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]
    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )
    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    yesterday = get_now() - timedelta(days=1)
    tomorrow = get_now() + timedelta(days=1)

    filtering_json = {
        "kv_pairs": [
            {
                "key": "creation_time",
                "min_value": yesterday.isoformat(),
                "max_value": tomorrow.isoformat(),
            },
        ],
        "columns": ["pulse_id", "device_id", "creation_time"],
    }

    response = client.post("/attrs/filter/", json=filtering_json)
    response_data = response.json()

    assert pulse_response.status_code == 200
    assert response.status_code == 200
    assert len(response_data) == 1
    assert response_data[0][0] == pulse_id
    assert response_data[0][1] == device_id
    assert isinstance(datetime.fromisoformat(response_data[0][2]), datetime)


def test_filter_no_kv_multiple_columns(client: TestClient, device_id: UUID) -> None:
    pulse_payload = [PulseCreate.create_mock(device_id=device_id).as_dict()]
    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )
    pulse_data = pulse_response.json()
    pulse_id = pulse_data[0]

    filtering_json = {
        "kv_pairs": [],
        "columns": ["pulse_id", "device_id"],
    }

    response = client.post("/attrs/filter/", json=filtering_json)
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data) == 1
    assert response_data[0][0] == pulse_id
    assert response_data[0][1] == device_id
