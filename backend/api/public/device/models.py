from __future__ import annotations

import re
from typing import Self

from pydantic import ConfigDict, field_validator
from sqlmodel import Field, SQLModel


class Device(SQLModel, table=True):
    """The table model for Devices.

    The purpose of this class is to interact with the database.
    """

    __tablename__ = "devices"

    device_id: str = Field(primary_key=True)

    @field_validator("device_id", mode="before")
    def validate_device_id(cls, value: str) -> str:  # noqa: N805
        """Validate a device_id.

        A valid device_id is a single capital letter, a hyphen, and four digits.
        """
        if not bool(re.match(r"^[A-Z]-\d{4}$", value)):
            msg = "Invalid device_id"
            raise ValueError(msg)
        return value


class DeviceCreate(Device):
    """The model for creating a new Device.

    As it does not take any other arguments than DeviceBase,
    it is only here for FastAPI documentation purposes.
    """

    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]

    @classmethod
    def create_mock(cls: type[DeviceCreate], device_id: str) -> DeviceCreate:
        return cls(device_id=device_id)

    def as_dict(self: Self) -> dict[str, str]:
        return self.model_dump()


class DeviceRead(Device):
    """The model for reading a Device.

    This model is for FastAPI calls that return a Device
    from the db, as this requires the device_id.
    """
