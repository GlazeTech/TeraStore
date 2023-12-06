from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from typing import Any, Self, TypedDict
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Float, SQLModel

from api.public.attrs.models import (
    AttrDict,
    PulseAttrs,
    TAttrReadDataType,
    TPulseAttrsCreate,
)
from api.utils.helpers import (
    generate_random_integration_time,
    generate_random_numbers,
    generate_scaled_numbers,
    get_now,
)


class TPulseDict(TypedDict):
    delays: list[float]
    signal: list[float]
    signal_error: list[float] | None
    integration_time_ms: int
    creation_time: str
    device_id: str
    pulse_attributes: list[AttrDict]


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
    signal_error: list[float] | None = Field(
        default=None,
        sa_column=Column(postgresql.ARRAY(Float)),
    )
    integration_time_ms: int
    creation_time: datetime
    device_id: UUID = Field(foreign_key="devices.device_id")


class Pulse(PulseBase, table=True):
    """Table model for Pulses.

    The purpose of this class is to interact with the database.
    """

    __tablename__ = "pulses"

    pulse_id: UUID = Field(default_factory=uuid4, primary_key=True)

    @staticmethod
    def create(
        pulse: dict[str, Any],
    ) -> Pulse:
        return Pulse(
            delays=pulse["delays"],
            signal=pulse["signal"],
            signal_error=pulse["signal_error"],
            integration_time_ms=pulse["integration_time_ms"],
            creation_time=pulse["creation_time"],
            device_id=pulse["device_id"],
        )


class PulseCreate(PulseBase):
    """Model for creating a new Pulse.

    As it does not take any other arguments than PulseBase,
    it is only here for FastAPI documentation purposes.
    """

    pulse_attributes: list[TPulseAttrsCreate]

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
            integration_time_ms=generate_random_integration_time(),
            creation_time=get_now(),
            device_id=device_id,
            pulse_attributes=[],
        )

    @classmethod
    def create_mock_w_errs(
        cls: type[PulseCreate],
        device_id: UUID,
        length: int = 600,
        timescale: float = 1e-10,
        amplitude: float = 100.0,
    ) -> PulseCreate:
        return cls(
            delays=generate_scaled_numbers(length, timescale),
            signal=generate_random_numbers(length, -amplitude, amplitude),
            signal_error=generate_random_numbers(
                length,
                -amplitude * 0.01,
                amplitude * 0.01,
            ),
            integration_time_ms=generate_random_integration_time(),
            creation_time=get_now(),
            device_id=device_id,
            pulse_attributes=[],
        )

    def as_dict(self: Self) -> TPulseDict:
        pulse_attributes = [
            pulse_attr.as_dict() for pulse_attr in self.pulse_attributes
        ]
        return {
            "delays": self.delays,
            "signal": self.signal,
            "signal_error": self.signal_error,
            "integration_time_ms": self.integration_time_ms,
            "creation_time": self.creation_time.isoformat(),
            "device_id": str(self.device_id),
            "pulse_attributes": pulse_attributes,
        }

    def create_pulse(self: Self) -> tuple[Pulse, PulseAttrs]:
        pulse = Pulse.create(self.model_dump(exclude={"pulse_attributes"}))
        pulse_attributes = PulseAttrs(
            pulse_id=pulse.pulse_id,
            pulse_attributes=self.pulse_attributes,
        )
        return pulse, pulse_attributes


class PulseRead(PulseBase):
    """Model for reading a Pulse.

    This model is for FastAPI calls that return a Pulse
    from the db, as this requires the pulse_id.
    """

    pulse_id: UUID


class AnnotatedPulseRead(PulseBase):
    """Model for reading a Pulse.

    This model is for FastAPI calls that return a Pulse
    from the db, as this requires the pulse_id.
    """

    pulse_id: UUID
    pulse_attributes: list[TAttrReadDataType]

    @classmethod
    def new(
        cls: type[AnnotatedPulseRead],
        pulse: Pulse,
        attrs: list[TAttrReadDataType],
    ) -> AnnotatedPulseRead:
        return cls(**pulse.model_dump(), pulse_attributes=attrs)


class TemporaryPulseIdTable(SQLModel, table=True):
    """Temporary table for performing joins on pulse IDs.

    Instead of using "SELECT .. WHERE id IN (...)"-style queries,
    adding the ID's to a temporary table first can drastically improve performance.

    See this: https://stackoverflow.com/questions/5803472/sql-where-id-in-id1-id2-idn
    """

    __tablename__ = "temporary_pulse_id_table"

    pulse_id: UUID = Field(default_factory=uuid4, primary_key=True)
