from __future__ import annotations

import re
from typing import Self, TypeAlias

from pydantic import StrictFloat, StrictStr, field_validator
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Float, SQLModel

from api.utils.exceptions import (
    DeviceStrAttrTooLongError,
    InvalidDeviceAttrKeyError,
    InvalidSerialNumberError,
)


class DeviceBase(SQLModel):
    """A Device is the data model representing a device that can create Pulses.

    This class is the base class for all Device related models.
    This is mostly for FastAPI's sake.
    See: https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/
    """

    serial_number: str = Field(unique=True, index=True)


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

    attrs: list[TDeviceAttr] | None = Field(default=None)

    @classmethod
    def create_mock(
        cls: type[DeviceCreate],
        serial_number: str,
        attrs: list[TDeviceAttr] | None = None,
    ) -> DeviceCreate:
        if attrs is None:
            attrs = []
        return cls.model_validate({"serial_number": serial_number, "attrs": attrs})

    def as_dict(self: Self) -> dict[str, str]:
        return self.model_dump()


class DeviceRead(DeviceBase):
    """The model for reading a Device.

    This model is for FastAPI calls that return a Device
    from the db, as this requires the device_id.
    """

    attributes: list[TDeviceAttr]

    @classmethod
    def new(
        cls: type[DeviceRead],
        device: Device,
        attributes: list[TDeviceAttr] | None = None,
    ) -> DeviceRead:
        if attributes is None:
            attributes = []
        return cls.model_validate({**device.model_dump(), "attributes": attributes})


class DeviceAttrBase(SQLModel):
    """Model for device attributes."""

    serial_number: str = Field(foreign_key="devices.serial_number", index=True)
    key: str

    @field_validator("key")
    def validate_key(cls, key: str) -> str:  # noqa: N805
        """Validate a device attribute key.

        Do not accept keys with special characters.
        """
        if not bool(re.match(r"^[a-zA-Z0-9_-]+$", key)):
            raise InvalidDeviceAttrKeyError(key)
        return key


class DeviceAttrStr(DeviceAttrBase):
    value: StrictStr

    @field_validator("value")
    def validate_value(cls, value: str) -> str:  # noqa: N805
        """Validate a string attribute.

        Do not accept strings larger than 200 characters.
        """
        max_length = 200
        if len(value) > max_length:
            raise DeviceStrAttrTooLongError(value)
        return value

    @property
    def table(self) -> type[SQLModel]:
        return _DeviceAttrStr


class DeviceAttrFloat(DeviceAttrBase):
    value: StrictFloat

    @property
    def table(self) -> type[SQLModel]:
        return _DeviceAttrFloat


class DeviceAttrFloatArray(DeviceAttrBase):
    value: list[float]

    @property
    def table(self) -> type[SQLModel]:
        return _DeviceAttrFloatArray


class _DeviceAttrStr(DeviceAttrStr, table=True):
    __tablename__ = "device_str_attrs"
    index: int | None = Field(default=None, primary_key=True)


class _DeviceAttrFloat(DeviceAttrFloat, table=True):
    __tablename__ = "device_float_attrs"
    index: int | None = Field(default=None, primary_key=True)


class _DeviceAttrFloatArray(DeviceAttrFloatArray, table=True):
    __tablename__ = "device_floatarray_attrs"
    value: list[float] = Field(sa_column=Column(postgresql.ARRAY(Float)))
    index: int | None = Field(default=None, primary_key=True)


TDeviceAttr: TypeAlias = DeviceAttrFloatArray | DeviceAttrFloat | DeviceAttrStr

TDeviceAttrTable: TypeAlias = _DeviceAttrFloatArray | _DeviceAttrFloat | _DeviceAttrStr


def device_attrs_tables() -> list[type[TDeviceAttrTable]]:
    return [_DeviceAttrFloatArray, _DeviceAttrFloat, _DeviceAttrStr]
