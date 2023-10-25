from uuid import UUID

from sqlmodel import Session

from api.database import engine
from api.public.attrs.models import PulseKeyRegistry, PulseStrAttrs
from api.public.device.models import Device, DeviceCreate
from api.public.pulse.models import Pulse, PulseCreate


def write_mock_device(device: DeviceCreate) -> Device:
    """Write a mock device to DB for testing purposes.

    Args:
    ----
        device (Device): The device to write.

    Returns:
    -------
        The written mock device.
    """
    device_to_db = Device.from_orm(device)
    with Session(engine) as session:
        session.add(device_to_db)
        session.commit()
        session.refresh(device_to_db)
    return device_to_db


def write_mock_pulse(pulse: PulseCreate) -> Pulse:
    """Write a mock pulse to DB for testing purposes.

    Args:
    ----
        pulse (Pulse): The pulse to write.

    Returns:
    -------
        The written pulse.
    """
    pulse_to_db = Pulse.from_orm(pulse)
    with Session(engine) as session:
        session.add(pulse_to_db)
        session.commit()
        session.refresh(pulse_to_db)
    return pulse_to_db


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
    device_g_1 = write_mock_device(DeviceCreate.create_mock("Glaze I"))
    device_g_2 = write_mock_device(DeviceCreate.create_mock("Glaze II"))
    device_carmen = write_mock_device(DeviceCreate.create_mock("Carmen"))

    pulse_1 = write_mock_pulse(
        PulseCreate.create_mock(device_id=device_g_1.device_id),
    )
    pulse_2 = write_mock_pulse(
        PulseCreate.create_mock(device_id=device_g_2.device_id),
    )
    pulse_3 = write_mock_pulse(
        PulseCreate.create_mock(device_id=device_carmen.device_id),
    )

    create_mock_attrs(pulse_1.pulse_id, "angle", "29")
    create_mock_attrs(pulse_1.pulse_id, "substrate", "sand-blasted steel")

    create_mock_attrs(pulse_2.pulse_id, "angle", "23")
    create_mock_attrs(pulse_2.pulse_id, "substrate", "plastic")

    create_mock_attrs(pulse_3.pulse_id, "angle", "17")
    create_mock_attrs(pulse_3.pulse_id, "substrate", "polymer")
