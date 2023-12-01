from uuid import UUID

from sqlmodel import Session

from api.database import app_engine
from api.public.attrs.crud import add_attr
from api.public.attrs.models import PulseAttrsFloatCreate, PulseAttrsStrCreate
from api.public.device.crud import create_device
from api.public.device.models import Device, DeviceCreate
from api.public.pulse.crud import create_pulses
from api.public.pulse.models import PulseCreate


def create_devices_and_pulses() -> None:
    """Create devices and pulses for testing purposes."""
    with Session(app_engine) as sess:
        device_g_1 = create_device(DeviceCreate.create_mock("Glaze I"), sess)
        device_g_2 = create_device(DeviceCreate.create_mock("Glaze II"), sess)
        device_carmen = create_device(DeviceCreate.create_mock("Carmen"), sess)

        pulse_1 = create_pulses(
            [PulseCreate.create_mock_w_errs(device_id=device_g_1.device_id)],
            sess,
        )
        pulse_2 = create_pulses(
            [PulseCreate.create_mock(device_id=device_g_2.device_id)],
            sess,
        )
        pulse_3 = create_pulses(
            [PulseCreate.create_mock(device_id=device_carmen.device_id)],
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
        device_g_1 = create_device(
            Device(
                friendly_name="Glaze I",
                # Device ID from glaze API
                device_id=UUID("5042dbda-e9bc-4216-a614-ac56d0a32023"),
            ),
            sess,
        )
        device_g_2 = create_device(
            Device(
                friendly_name="Glaze II",
                # Device ID from glaze API
                device_id=UUID("66fa482a-1ef4-4076-a883-72d7bf43e151"),
            ),
            sess,
        )
        device_carmen = create_device(
            Device(
                friendly_name="Carmen",
                # Device ID from glaze API
                device_id=UUID("6a54db26-fa88-4146-b04f-b84b945bfea8"),
            ),
            sess,
        )

        projects = {
            "CGM": 5,
            "graphene": 8,
            "hempel": 13,
        }
        count = 0
        for project, n_pulses in projects.items():
            pulses = [
                PulseCreate.create_mock(
                    device_id=device_carmen.device_id
                    if count % 3 == 0
                    else device_g_2.device_id,
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
            [PulseCreate.create_mock(device_id=device_g_1.device_id)],
            sess,
        )
        pulse_2 = create_pulses(
            [PulseCreate.create_mock(device_id=device_g_2.device_id)],
            sess,
        )
        pulse_3 = create_pulses(
            [PulseCreate.create_mock(device_id=device_carmen.device_id)],
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

        add_attr(pulse_3[0], PulseAttrsFloatCreate(key="angle", value=17.2), sess)
        add_attr(
            pulse_3[0],
            PulseAttrsStrCreate(key="substrate", value="polymer"),
            sess,
        )
