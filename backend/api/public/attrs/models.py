from __future__ import annotations

from enum import Enum

from pydantic.types import StrictFloat, StrictStr
from sqlmodel import Field, SQLModel

from api.utils.exceptions import AttrDataTypeDoesNotExistError

# Must be defined early in file to avoid Pydantic panic
attr_data_type = StrictStr | StrictFloat
attr_data_type_list = list[StrictStr] | list[StrictFloat]


class AttrDataType(str, Enum):
    """Enum for attribute data types."""

    STRING = "string"
    FLOAT = "float"


class PulseAttrsBase(SQLModel):
    key: str


class PulseAttrsReadBase(SQLModel):
    key: str


class PulseAttrsCreateBase(SQLModel):
    key: str
    data_type: AttrDataType
    value: attr_data_type


class PulseAttrsFilterBase(SQLModel):
    key: str


class PulseAttrsStr(PulseAttrsBase, table=True):
    """The purpose of this class is to interact with the database."""

    __tablename__ = "pulse_str_attrs"

    value: StrictStr
    pulse_id: int = Field(foreign_key="pulses.pulse_id", index=True)

    index: int | None = Field(default=None, primary_key=True)


class PulseAttrsStrRead(PulseAttrsReadBase):
    value: StrictStr


class PulseAttrsStrCreate(PulseAttrsCreateBase):
    value: StrictStr
    data_type: AttrDataType = Field(default=AttrDataType.STRING.value)


class PulseAttrsStrFilter(PulseAttrsFilterBase):
    value: StrictStr


class PulseAttrsFloat(PulseAttrsBase, table=True):
    """The purpose of this class is to interact with the database."""

    __tablename__ = "pulse_float_attrs"

    value: StrictFloat
    pulse_id: int = Field(foreign_key="pulses.pulse_id", index=True)

    index: int | None = Field(default=None, primary_key=True)


class PulseAttrsFloatRead(PulseAttrsReadBase):
    value: StrictFloat


class PulseAttrsFloatCreate(PulseAttrsCreateBase):
    value: StrictFloat
    data_type: AttrDataType = Field(default=AttrDataType.FLOAT.value)


class PulseAttrsFloatFilter(PulseAttrsFilterBase):
    min_value: StrictFloat
    max_value: StrictFloat


# Has to be defined after definition of both classes
attr_read_data_type = PulseAttrsStrRead | PulseAttrsFloatRead
attr_filter_data_type = PulseAttrsStrFilter | PulseAttrsFloatFilter


# Factory function for finding the correct PulseAttrs class
def get_pulse_attrs_class(
    data_type: AttrDataType,
) -> type[PulseAttrsStr | PulseAttrsFloat]:
    """Return the correct PulseAttrs table class based on instance data type."""
    if data_type == AttrDataType.STRING:
        return PulseAttrsStr
    if data_type == AttrDataType.FLOAT:
        return PulseAttrsFloat
    raise AttrDataTypeDoesNotExistError(data_type=data_type.value)


def get_pulse_attrs_read_class(
    data_type: AttrDataType,
) -> type[PulseAttrsStrRead | PulseAttrsFloatRead]:
    if data_type == AttrDataType.STRING:
        return PulseAttrsStrRead
    if data_type == AttrDataType.FLOAT:
        return PulseAttrsFloatRead
    raise AttrDataTypeDoesNotExistError(data_type=data_type.value)


class PulseKeyRegistry(SQLModel, table=True):
    """Table model for Pulse EAV key registry."""

    __tablename__ = "pulse_key_registry"

    key: str
    data_type: str

    index: int | None = Field(default=None, primary_key=True)
