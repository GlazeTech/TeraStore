from __future__ import annotations

import re
from typing import Self

from pydantic import ConfigDict, field_validator
from sqlmodel import Field, SQLModel

from api.utils.exceptions import InvalidSerialNumberError


class DeviceBase(SQLModel):
    """A Device is the data model representing a device that can create Pulses.

    This class is the base class for all Device related models.
    This is mostly for FastAPI's sake.
    See: https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/
    """

    serial_number: str = Field(unique=True)


class Device(DeviceBase, table=True):
    """The table model for Devices.

    The purpose of this class is to interact with the database.
    """

    __tablename__ = "devices"

    device_id: int | None = Field(default=None, primary_key=True)

    @field_validator("serial_number")
    def validate_device_id(cls, value: str) -> str:  # noqa: N805
        """Validate a device_id.

        A valid device_id is a single capital letter, a hyphen, and four digits.
        """
        if not bool(re.match(r"^[A-Z]-\d{4}$", value)):
            raise InvalidSerialNumberError(value)
        return value


class DeviceCreate(DeviceBase):
    """The model for creating a new Device.

    As it does not take any other arguments than DeviceBase,
    it is only here for FastAPI documentation purposes.
    """

    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]

    @classmethod
    def create_mock(cls: type[DeviceCreate], serial_number: str) -> DeviceCreate:
        return cls(serial_number=serial_number)

    def as_dict(self: Self) -> dict[str, str]:
        return self.model_dump()


class DeviceRead(DeviceBase):
    """The model for reading a Device.

    This model is for FastAPI calls that return a Device
    from the db, as this requires the device_id.
    """
