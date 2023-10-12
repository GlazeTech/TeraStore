from datetime import datetime
from uuid import UUID

import numpy as np
import pytz
from sqlmodel import Session

from api.database import engine
from api.public.device.models import Device
from api.public.pulse.models import Pulse

rng = np.random.default_rng()


def create_mock_device(friendly_name: str) -> Device:
    """Create a mock device for testing purposes."""
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
    """Create a mock pulse for testing purposes."""
    with Session(engine) as session:
        now = datetime.now(tz=pytz.timezone("Europe/Copenhagen"))
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
        delays=(np.linspace(0, 100, 600) * 1e-10).tolist(),
        signal=rng.random(size=(600,)).tolist(),
        integration_time=6000,
        device_id=device_g_1.device_id,
    )
    create_mock_pulse(
        delays=(np.linspace(0, 100, 600) * 1e-10).tolist(),
        signal=rng.random(size=(600,)).tolist(),
        integration_time=3000,
        device_id=device_g_2.device_id,
    )
    create_mock_pulse(
        delays=(np.linspace(0, 100, 600) * 1e-10).tolist(),
        signal=rng.random(size=(600,)).tolist(),
        integration_time=2000,
        device_id=device_carmen.device_id,
    )
