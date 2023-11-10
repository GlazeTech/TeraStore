from fastapi.testclient import TestClient

from api.utils.mock_data_generator import create_devices_and_pulses


def test_get_all_keys(client: TestClient) -> None:
    create_devices_and_pulses()

    response = client.get("/attrs/keys/")

    assert response.status_code == 200
    assert response.json() == ["angle", "substrate"]


def test_get_all_values_on_key(client: TestClient) -> None:
    create_devices_and_pulses()

    response = client.get("/attrs/angle/values/")

    assert response.status_code == 200
    assert response.json() == ["17", "23", "29"]


def test_get_all_values_on_non_existing_key(client: TestClient) -> None:
    create_devices_and_pulses()

    response = client.get("/attrs/non-existing-key/values/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_attrs_on_pulse(client: TestClient, device_uuid: str) -> None:
    pulse_payload = {
        "device_id": device_uuid,
        "delays": [1, 2, 3],
        "signal": [1, 2, 3],
        "integration_time": 100,
        "creation_time": "2021-01-01T00:00:00",
    }
    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )
    pulse_data = pulse_response.json()

    attrs_1_key = "angle"
    attrs_1_value = "29"

    client.put(
        f"/pulses/{pulse_data['pulse_id']}/attrs?key={attrs_1_key}&value={attrs_1_value}",
    )

    attrs_2_key = "substrate"
    attrs_2_value = "sand-blasted steel"

    client.put(
        f"/pulses/{pulse_data['pulse_id']}/attrs?key={attrs_2_key}&value={attrs_2_value}",
    )

    response = client.get(f"/pulses/{pulse_data['pulse_id']}/attrs/")
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data) == 2
    assert response_data[0]["key"] == attrs_1_key
    assert response_data[0]["value"] == attrs_1_value
    assert response_data[1]["key"] == attrs_2_key
    assert response_data[1]["value"] == attrs_2_value


def test_get_pulse_attrs_on_non_existing_pulse(client: TestClient) -> None:
    pulse_id = 1000
    response = client.get(f"/pulses/{pulse_id}/attrs/")

    assert response.status_code == 404
    assert response.json()["detail"] == f"Pulse not found with id: {pulse_id}"


def test_add_pulse_attrs_on_pulse(client: TestClient, device_uuid: str) -> None:
    pulse_payload = {
        "device_id": device_uuid,
        "delays": [1, 2, 3],
        "signal": [1, 2, 3],
        "integration_time": 100,
        "creation_time": "2021-01-01T00:00:00",
    }
    pulse_response = client.post(
        "/pulses/create/",
        json=pulse_payload,
    )
    pulse_data = pulse_response.json()

    attrs_key = "angle"
    attrs_value = "29"

    client.put(
        f"/pulses/{pulse_data['pulse_id']}/attrs?key={attrs_key}&value={attrs_value}",
    )

    response = client.get(f"/pulses/{pulse_data['pulse_id']}/attrs/")
    response_data = response.json()

    assert response.status_code == 200
    assert response_data[0]["key"] == attrs_key
    assert response_data[0]["value"] == attrs_value


def test_add_pulse_attrs_on_non_existing_pulse(client: TestClient) -> None:
    pulse_id = 1000
    attrs_key = "angle"
    attrs_value = "29"

    response = client.put(
        f"/pulses/{pulse_id}/attrs?key={attrs_key}&value={attrs_value}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == f"Pulse not found with id: {pulse_id}"
