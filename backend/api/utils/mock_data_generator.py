from sqlmodel import Session

from api.database import app_engine
from api.public.attrs.crud import create_attr
from api.public.attrs.models import KeyValuePair
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

        create_attr(
            pulse_1.pulse_id,
            KeyValuePair(key="angle", value="29", data_type="string"),
            sess,
        )
        create_attr(
            pulse_1.pulse_id,
            KeyValuePair(
                key="substrate",
                value="sand-blasted steel",
                data_type="string",
            ),
            sess,
        )

        create_attr(
            pulse_2.pulse_id,
            KeyValuePair(key="angle", value="23", data_type="string"),
            sess,
        )
        create_attr(
            pulse_2.pulse_id,
            KeyValuePair(key="substrate", value="plastic", data_type="string"),
            sess,
        )

        create_attr(
            pulse_3.pulse_id,
            KeyValuePair(key="angle", value="17", data_type="string"),
            sess,
        )
        create_attr(
            pulse_3.pulse_id,
            KeyValuePair(key="substrate", value="polymer", data_type="string"),
            sess,
        )


def create_frontend_dev_data() -> None:
    """Create devices and pulses for testing purposes."""
    with Session(app_engine) as sess:
        device_g_1 = create_device(DeviceCreate.create_mock("Glaze I"), sess)
        device_g_2 = create_device(DeviceCreate.create_mock("Glaze II"), sess)
        device_carmen = create_device(DeviceCreate.create_mock("Carmen"), sess)

        projects = {
            "CGM": 5,
            "graphene": 8,
            "hempel": 13,
        }
        count = 0
        for project, n_pulses in projects.items():
            pulses = [
                create_pulse(
                    PulseCreate.create_mock(
                        device_id=device_carmen.device_id
                        if count % 3 == 0
                        else device_g_2.device_id,
                    ),
                    sess,
                )
                for _ in range(n_pulses)
            ]
            for pulse in pulses:
                create_attr(
                    pulse_id=pulse.pulse_id,
                    kv_pair=KeyValuePair(
                        key="project",
                        value=project,
                        data_type="string",
                    ),
                    db=sess,
                )
                if count % 2 == 0:
                    create_attr(
                        pulse_id=pulse.pulse_id,
                        kv_pair=KeyValuePair(
                            key="substrate",
                            value="PMMA",
                            data_type="string",
                        ),
                        db=sess,
                    )
                if count % 2 == 1:
                    create_attr(
                        pulse_id=pulse.pulse_id,
                        kv_pair=KeyValuePair(
                            key="spotsize (mm)",
                            value="5.6",
                            data_type="string",
                        ),
                        db=sess,
                    )
                if count % 3 == 0:
                    create_attr(
                        pulse_id=pulse.pulse_id,
                        kv_pair=KeyValuePair(
                            key="mode",
                            value="reflection",
                            data_type="string",
                        ),
                        db=sess,
                    )
                else:
                    create_attr(
                        pulse_id=pulse.pulse_id,
                        kv_pair=KeyValuePair(
                            key="mode",
                            value="transmission",
                            data_type="string",
                        ),
                        db=sess,
                    )
                if count % 5 == 0:
                    create_attr(
                        pulse_id=pulse.pulse_id,
                        kv_pair=KeyValuePair(
                            key="antennas",
                            value="HHI",
                            data_type="string",
                        ),
                        db=sess,
                    )
                else:
                    create_attr(
                        pulse_id=pulse.pulse_id,
                        kv_pair=KeyValuePair(
                            key="antennas",
                            value="Toptica",
                            data_type="string",
                        ),
                        db=sess,
                    )
                count += 1

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

        create_attr(
            pulse_1.pulse_id,
            KeyValuePair(key="angle", value="29", data_type="string"),
            sess,
        )
        create_attr(
            pulse_1.pulse_id,
            KeyValuePair(
                key="substrate",
                value="sand-blasted steel",
                data_type="string",
            ),
            sess,
        )

        create_attr(
            pulse_2.pulse_id,
            KeyValuePair(key="angle", value="23", data_type="string"),
            sess,
        )
        create_attr(
            pulse_2.pulse_id,
            KeyValuePair(key="substrate", value="plastic", data_type="string"),
            sess,
        )

        create_attr(
            pulse_3.pulse_id,
            KeyValuePair(key="angle", value="17", data_type="string"),
            sess,
        )
        create_attr(
            pulse_3.pulse_id,
            KeyValuePair(key="substrate", value="polymer", data_type="string"),
            sess,
        )
