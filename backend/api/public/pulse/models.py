from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Float, SQLModel

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

    pulse_id: UUID = Field(default_factory=uuid4, primary_key=True)


class PulseCreate(PulseBase):
    """Model for creating a new Pulse.

    As it does not take any other arguments than PulseBase,
    it is only here for FastAPI documentation purposes.
    """


class PulseRead(PulseBase):
    """Model for reading a Pulse.

    This model is for FastAPI calls that return a Pulse
    from the db, as this requires the pulse_id.
    """

    pulse_id: UUID


class PulseReadWithDevice(PulseRead):
    """Model for reading a Pulse with its Device."""

    device: DeviceRead
