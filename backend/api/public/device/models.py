from __future__ import annotations

from typing import Self
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class DeviceBase(SQLModel):
    """A Device is the data model representing a device that can create Pulses.

    This class is the base class for all Device related models.
    This is mostly for FastAPI's sake.
    See: https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/
    """

    friendly_name: str


class Device(DeviceBase, table=True):
    """The table model for Devices.

    The purpose of this class is to interact with the database.
    """

    __tablename__ = "devices"

    device_id: UUID = Field(default_factory=uuid4, primary_key=True)


class DeviceCreate(DeviceBase):
    """The model for creating a new Device.

    As it does not take any other arguments than DeviceBase,
    it is only here for FastAPI documentation purposes.
    """

    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]

    @classmethod
    def create_mock(cls: type[DeviceCreate], friendly_name: str) -> DeviceCreate:
        return cls(friendly_name=friendly_name)

    def as_dict(self: Self) -> dict[str, str]:
        return self.model_dump()


class DeviceRead(DeviceBase):
    """The model for reading a Device.

    This model is for FastAPI calls that return a Device
    from the db, as this requires the device_id.
    """

    device_id: UUID
