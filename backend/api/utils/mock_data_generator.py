import secrets
from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlmodel import Session

from api.database import engine
from api.public.device.models import Device
from api.public.pulse.models import Pulse


def generate_random_numbers(
    n: int,
    lower_bound: int,
    upper_bound: int,
) -> list[float]:
    """Generate list of n random integers between lower_bound and upper_bound.

    Args:
    ----
        n (int): The number of random integers to generate.
        lower_bound (int): The lower bound (inclusive) for the random integers.
        upper_bound (int): The upper bound (exclusive) for the random integers.

    Returns:
    -------
        A list of random integers.
    """
    return [secrets.SystemRandom().uniform(lower_bound, upper_bound) for _ in range(n)]


def generate_scaled_numbers(n: int, scale_factor: float) -> list[float]:
    """Generate a list of numbers from 0 to < n and multiply each by scale_factor.

    Args:
    ----
        n (int): The upper limit (exclusive) for the numbers.
        scale_factor (float): The factor to multiply each number with.

    Returns:
    -------
        A list of scaled numbers.
    """
    return [i * scale_factor for i in range(n)]


def create_mock_device(friendly_name: str) -> Device:
    """Create a mock device for testing purposes.

    Args:
    ----
        friendly_name (str): The friendly name of the device.

    Returns:
    -------
        A mock device.
    """
    with Session(engine) as session:
        device = Device(friendly_name=friendly_name)
        session.add(device)
        session.commit()
        session.refresh(device)
        return device


def create_mock_pulse(
    delays: list[float],
    signal: list[float],
    integration_time: int,
    device_id: UUID,
) -> Pulse:
    """Create a mock pulse for testing purposes.

    Args:
    ----
        delays (list[float]): A list of delays.
        signal (list[float]): A list of signals.
        integration_time (int): The integration time of the pulse.
        device_id (UUID): The id of the device that created the pulse.

    Returns:
    -------
        A mock pulse.
    """
    with Session(engine) as session:
        now = datetime.now(tz=ZoneInfo("Europe/Copenhagen"))
        pulse = Pulse(
            delays=delays,
            signal=signal,
            integration_time=integration_time,
            creation_time=now,
            device_id=device_id,
        )
        session.add(pulse)
        session.commit()
        session.refresh(pulse)
        return pulse


def create_devices_and_pulses() -> None:
    """Create devices and pulses for testing purposes."""
    device_g_1 = create_mock_device("Glaze I")
    device_g_2 = create_mock_device("Glaze II")
    device_carmen = create_mock_device("Carmen")

    create_mock_pulse(
        delays=generate_scaled_numbers(600, 1e-10),
        signal=generate_random_numbers(600, 0, 100),
        integration_time=6000,
        device_id=device_g_1.device_id,
    )
    create_mock_pulse(
        delays=generate_scaled_numbers(600, 1e-10),
        signal=generate_random_numbers(600, 0, 100),
        integration_time=3000,
        device_id=device_g_2.device_id,
    )
    create_mock_pulse(
        delays=generate_scaled_numbers(600, 1e-10),
        signal=generate_random_numbers(600, 0, 100),
        integration_time=2000,
        device_id=device_carmen.device_id,
    )
