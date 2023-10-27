from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from typing import TYPE_CHECKING, Self
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Float, SQLModel

from api.utils.helpers import (
    generate_random_integration_time,
    generate_random_numbers,
    generate_scaled_numbers,
    get_now,
)

if TYPE_CHECKING:
    from api.public.device.models import DeviceRead


class PulseBase(SQLModel):
    """A Pulse is the data model representing a single pulse create by some Device.

    It is essentially a collection of delays and signal values, along with some
    metadata.

    To work with arrays in Postgres, we need to use the postgresql.ARRAY type
    from sqlalchemy.dialects. This is a custom type that is not supported by
    the SQLModel library.
    See https://github.com/tiangolo/sqlmodel/issues/178.

    This class is the base class for all Pulse related models.
    This is mostly for FastAPI's sake.
    See: https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/
    """

    delays: list[float] = Field(sa_column=Column(postgresql.ARRAY(Float)))
    signal: list[float] = Field(sa_column=Column(postgresql.ARRAY(Float)))
    integration_time: int
    creation_time: datetime
    device_id: UUID = Field(foreign_key="device.device_id")


class Pulse(PulseBase, table=True):
    """Table model for Pulses.

    The purpose of this class is to interact with the database.
    """

    __tablename__ = "pulses"

    pulse_id: UUID = Field(default_factory=uuid4, primary_key=True)


class PulseCreate(PulseBase):
    """Model for creating a new Pulse.

    As it does not take any other arguments than PulseBase,
    it is only here for FastAPI documentation purposes.
    """

    @classmethod
    def create_mock(
        cls: type[PulseCreate],
        device_id: UUID,
        length: int = 600,
        timescale: float = 1e-10,
        amplitude: float = 100.0,
    ) -> PulseCreate:
        return cls(
            delays=generate_scaled_numbers(length, timescale),
            signal=generate_random_numbers(length, -amplitude, amplitude),
            integration_time=generate_random_integration_time(),
            creation_time=get_now(),
            device_id=device_id,
        )

    def as_dict(self: Self) -> dict[str, list[float] | int | str | UUID]:
        return {
            "delays": self.delays,
            "signal": self.signal,
            "integration_time": self.integration_time,
            "creation_time": self.creation_time.isoformat(),
            "device_id": str(self.device_id),
        }


class PulseRead(PulseBase):
    """Model for reading a Pulse.

    This model is for FastAPI calls that return a Pulse
    from the db, as this requires the pulse_id.
    """

    pulse_id: UUID


class PulseReadWithDevice(PulseRead):
    """Model for reading a Pulse with its Device."""

    device: DeviceRead
