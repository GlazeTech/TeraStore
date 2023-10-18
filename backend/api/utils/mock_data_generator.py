from uuid import UUID

from sqlmodel import Session

from api.database import engine
from api.public.attrs.models import PulseKeyRegistry, PulseStrAttrs
from api.public.device.models import Device
from api.public.pulse.models import Pulse
from api.utils.helpers import generate_random_numbers, generate_scaled_numbers, get_now


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
        now = get_now()
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


def create_mock_attrs(pulse_id: UUID, key: str, value: str) -> None:
    """Create mock attributes for testing purposes.

    Args:
    ----
        pulse_id (UUID): The id of the pulse.
        key (str): The key of the attribute.
        value (str): The value of the attribute.

    Returns:
    -------
        None
    """
    with Session(engine) as session:
        existing_key = (
            session.query(PulseKeyRegistry).filter(PulseKeyRegistry.key == key).first()
        )
        if not existing_key:
            new_key = PulseKeyRegistry(key=key)
            session.add(new_key)
        attrs = PulseStrAttrs(pulse_id=pulse_id, key=key, value=value)
        session.add(attrs)
        session.commit()
        session.refresh(attrs)


def create_devices_and_pulses() -> None:
    """Create devices and pulses for testing purposes."""
    device_g_1 = create_mock_device("Glaze I")
    device_g_2 = create_mock_device("Glaze II")
    device_carmen = create_mock_device("Carmen")

    pulse_1 = create_mock_pulse(
        delays=generate_scaled_numbers(600, 1e-10),
        signal=generate_random_numbers(600, 0, 100),
        integration_time=6000,
        device_id=device_g_1.device_id,
    )
    pulse_2 = create_mock_pulse(
        delays=generate_scaled_numbers(600, 1e-10),
        signal=generate_random_numbers(600, 0, 100),
        integration_time=3000,
        device_id=device_g_2.device_id,
    )
    pulse_3 = create_mock_pulse(
        delays=generate_scaled_numbers(600, 1e-10),
        signal=generate_random_numbers(600, 0, 100),
        integration_time=2000,
        device_id=device_carmen.device_id,
    )

    create_mock_attrs(pulse_1.pulse_id, "angle", "29")
    create_mock_attrs(pulse_1.pulse_id, "substrate", "sand-blasted steel")

    create_mock_attrs(pulse_2.pulse_id, "angle", "23")
    create_mock_attrs(pulse_2.pulse_id, "substrate", "plastic")

    create_mock_attrs(pulse_3.pulse_id, "angle", "17")
    create_mock_attrs(pulse_3.pulse_id, "substrate", "polymer")
