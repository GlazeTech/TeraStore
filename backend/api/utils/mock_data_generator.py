from sqlmodel import Session

from api.database import app_engine
from api.public.attrs.crud import add_attr
from api.public.attrs.models import PulseAttrsFloatCreate, PulseAttrsStrCreate
from api.public.auth.crud import create_user
from api.public.auth.models import AuthLevel, UserCreate
from api.public.device.crud import create_device
from api.public.device.models import Device, DeviceCreate
from api.public.pulse.crud import create_pulses
from api.public.pulse.models import PulseCreate


def create_devices_and_pulses() -> None:
    """Create devices and pulses for testing purposes."""
    with Session(app_engine) as sess:
        device_g_1 = create_device(DeviceCreate.create_mock("G-0001"), sess)
        device_g_2 = create_device(DeviceCreate.create_mock("G-0002"), sess)
        device_carmen = create_device(DeviceCreate.create_mock("C-0001"), sess)

        pulse_1 = create_pulses(
            [
                PulseCreate.create_mock_w_errs(
                    device_serial_number=device_g_1.serial_number
                )
            ],
            sess,
        )
        pulse_2 = create_pulses(
            [PulseCreate.create_mock(device_serial_number=device_g_2.serial_number)],
            sess,
        )
        pulse_3 = create_pulses(
            [PulseCreate.create_mock(device_serial_number=device_carmen.serial_number)],
            sess,
        )
        add_attr(pulse_1[0], PulseAttrsFloatCreate(key="has_errors", value=1.0), sess)
        add_attr(pulse_1[0], PulseAttrsFloatCreate(key="angle", value=29.0), sess)
        add_attr(
            pulse_1[0],
            PulseAttrsStrCreate(key="substrate", value="sand-blasted steel"),
            sess,
        )
        add_attr(
            pulse_1[0],
            PulseAttrsFloatCreate(key="angle", value=17.1),
            sess,
        )

        add_attr(pulse_2[0], PulseAttrsFloatCreate(key="angle", value=23.2), sess)
        add_attr(
            pulse_2[0],
            PulseAttrsStrCreate(key="substrate", value="plastic"),
            sess,
        )

        add_attr(pulse_3[0], PulseAttrsFloatCreate(key="angle", value=24.5), sess)
        add_attr(
            pulse_3[0],
            PulseAttrsStrCreate(key="substrate", value="polymer"),
            sess,
        )


def create_frontend_dev_data() -> None:
    """Create devices and pulses for testing purposes."""
    with Session(app_engine) as sess:
        create_user(
            UserCreate(email="admin@admin", password="admin"),  # noqa: S106
            auth_level=AuthLevel.ADMIN,
            db=sess,
        )
        device_g_1 = create_device(Device(serial_number="G-0003"), sess)
        device_g_2 = create_device(Device(serial_number="G-0004"), sess)

        projects = {
            "CGM": 5,
            "graphene": 8,
            "hempel": 13,
        }
        count = 0
        for project, n_pulses in projects.items():
            pulses = [
                PulseCreate.create_mock(
                    device_serial_number=device_g_1.serial_number
                    if count % 3 == 0
                    else device_g_2.serial_number,
                )
                for _ in range(n_pulses)
            ]
            pulse_ids = create_pulses(pulses, sess)
            for pulse_id in pulse_ids:
                add_attr(
                    pulse_id=pulse_id,
                    kv_pair=PulseAttrsStrCreate(key="project", value=project),
                    db=sess,
                )
                if count % 2 == 0:
                    add_attr(
                        pulse_id=pulse_id,
                        kv_pair=PulseAttrsStrCreate(key="substrate", value="PMMA"),
                        db=sess,
                    )
                if count % 2 == 1:
                    add_attr(
                        pulse_id=pulse_id,
                        kv_pair=PulseAttrsFloatCreate(key="spotsize (mm)", value=5.6),
                        db=sess,
                    )
                if count % 3 == 0:
                    add_attr(
                        pulse_id=pulse_id,
                        kv_pair=PulseAttrsStrCreate(key="mode", value="reflection"),
                        db=sess,
                    )
                else:
                    add_attr(
                        pulse_id=pulse_id,
                        kv_pair=PulseAttrsStrCreate(key="mode", value="transmission"),
                        db=sess,
                    )
                if count % 5 == 0:
                    add_attr(
                        pulse_id=pulse_id,
                        kv_pair=PulseAttrsStrCreate(key="antennas", value="HHI"),
                        db=sess,
                    )
                else:
                    add_attr(
                        pulse_id=pulse_id,
                        kv_pair=PulseAttrsStrCreate(key="antennas", value="Toptica"),
                        db=sess,
                    )
                count += 1

        pulse_1 = create_pulses(
            [PulseCreate.create_mock(device_serial_number=device_g_1.serial_number)],
            sess,
        )
        pulse_2 = create_pulses(
            [PulseCreate.create_mock(device_serial_number=device_g_2.serial_number)],
            sess,
        )

        add_attr(pulse_1[0], PulseAttrsFloatCreate(key="angle", value=29.0), sess)
        add_attr(
            pulse_1[0],
            PulseAttrsStrCreate(key="substrate", value="sand-blasted steel"),
            sess,
        )

        add_attr(pulse_2[0], PulseAttrsFloatCreate(key="angle", value=23.0), sess)
        add_attr(
            pulse_2[0],
            PulseAttrsStrCreate(key="substrate", value="plastic"),
            sess,
        )
