from sqlmodel import Session

from api.database import app_engine
from api.public.attrs.crud import add_str_attr
from api.public.device.crud import create_device
from api.public.device.models import DeviceCreate
from api.public.pulse.crud import create_pulse
from api.public.pulse.models import PulseCreate


def create_devices_and_pulses() -> None:
    """Create devices and pulses for testing purposes."""
    with Session(app_engine) as sess:
        device_g_1 = create_device(DeviceCreate.create_mock("Glaze I"), sess)
        device_g_2 = create_device(DeviceCreate.create_mock("Glaze II"), sess)
        device_carmen = create_device(DeviceCreate.create_mock("Carmen"), sess)

        pulse_1 = create_pulse(
            PulseCreate.create_mock(device_id=device_g_1.device_id),
            sess,
        )
        pulse_2 = create_pulse(
            PulseCreate.create_mock(device_id=device_g_2.device_id),
            sess,
        )
        pulse_3 = create_pulse(
            PulseCreate.create_mock(device_id=device_carmen.device_id),
            sess,
        )

        add_str_attr(pulse_1.pulse_id, "angle", "29", sess)
        add_str_attr(pulse_1.pulse_id, "substrate", "sand-blasted steel", sess)

        add_str_attr(pulse_2.pulse_id, "angle", "23", sess)
        add_str_attr(pulse_2.pulse_id, "substrate", "plastic", sess)

        add_str_attr(pulse_3.pulse_id, "angle", "17", sess)
        add_str_attr(pulse_3.pulse_id, "substrate", "polymer", sess)
