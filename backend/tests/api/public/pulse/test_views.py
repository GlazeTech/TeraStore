from fastapi.testclient import TestClient

from api.utils.helpers import generate_random_numbers, generate_scaled_numbers, get_now


def test_create_pulse(client: TestClient) -> None:
    """Test that a pulse can be created."""
    response = client.post(
        "/devices/",
        json={"friendly_name": "Glaze I"},
    )
    data = response.json()
    device_id = data["device_id"]

    # Right now it seems we're not using timezones in the database
    now = get_now().isoformat().split("+")[0]
    response = client.post(
        "/pulses/",
        json={
            "delays": generate_scaled_numbers(100, 1e-10),
            "signal": generate_random_numbers(100, 0, 100),
            "integration_time": 3000,
            "creation_time": now,
            "device_id": device_id,
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["device_id"] == device_id
    assert len(data["delays"]) == 100
    assert len(data["signal"]) == 100
    assert data["integration_time"] == 3000
    assert data["creation_time"] == now
    assert data["pulse_id"] is not None


def test_get_pulse(client: TestClient) -> None:
    """Test that a pulse can be retrieved."""
    response = client.post(
        "/devices/",
        json={"friendly_name": "Glaze I"},
    )
    data = response.json()
    device_id = data["device_id"]

    # Right now it seems we're not using timezones in the database
    now = get_now().isoformat().split("+")[0]
    response = client.post(
        "/pulses/",
        json={
            "delays": generate_scaled_numbers(100, 1e-10),
            "signal": generate_random_numbers(100, 0, 100),
            "integration_time": 3000,
            "creation_time": now,
            "device_id": device_id,
        },
    )
    data = response.json()
    pulse_id = data["pulse_id"]

    response = client.get(f"/pulses/{pulse_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["device_id"] == device_id
    assert len(data["delays"]) == 100
    assert len(data["signal"]) == 100
    assert data["integration_time"] == 3000
    assert data["creation_time"] == now
    assert data["pulse_id"] == pulse_id
