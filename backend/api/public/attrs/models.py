from __future__ import annotations

from collections.abc import Sequence

# Ruff wants this import to be in a TYPE_CHECKING block
# THIS WILL BREAK PYDANTIC, DO NO DO IT
from datetime import datetime  # noqa: TCH003
from enum import Enum
from typing import Self, TypeAlias, TypedDict
from uuid import UUID, uuid4

from pydantic import BaseModel
from pydantic.types import StrictFloat, StrictInt, StrictStr
from sqlmodel import Field, SQLModel

from api.utils.exceptions import AttrDataTypeDoesNotExistError

# Must be defined early in file to avoid Pydantic panic
# As soon as Mypy supports PEP 695, we should implement the new type syntax
# See: https://github.com/python/mypy/issues/15238
TAttrDataType: TypeAlias = StrictStr | StrictFloat
TAttrDataTypeList: TypeAlias = Sequence[StrictStr] | Sequence[StrictFloat]
TPulseAttr: TypeAlias = float | str


class AttrDict(TypedDict):
    key: str
    value: TAttrDataType
    data_type: AttrDataType


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
    value: TAttrDataType


class PulseAttrsFilterBase(SQLModel):
    key: str


class PulseAttrsStr(PulseAttrsBase, table=True):
    """The purpose of this class is to interact with the database."""

    __tablename__ = "pulse_str_attrs"

    value: StrictStr
    pulse_id: UUID = Field(foreign_key="pulses.pulse_id", index=True)

    index: UUID = Field(default_factory=uuid4, primary_key=True)


class PulseAttrsStrRead(PulseAttrsReadBase):
    value: StrictStr


class PulseAttrsStrCreate(PulseAttrsCreateBase):
    value: StrictStr
    data_type: AttrDataType = Field(default=AttrDataType.STRING.value)

    @classmethod
    def create_mock(
        cls: type[PulseAttrsStrCreate],
        key: str = "mock_string_key",
        value: str = "mock_string_value",
    ) -> PulseAttrsStrCreate:
        return cls(key=key, value=value)

    def as_dict(self: Self) -> AttrDict:
        return {"key": self.key, "value": self.value, "data_type": self.data_type}


class PulseAttrsStrFilter(PulseAttrsFilterBase):
    value: StrictStr


class PulseAttrsFloat(PulseAttrsBase, table=True):
    """The purpose of this class is to interact with the database."""

    __tablename__ = "pulse_float_attrs"

    value: StrictFloat
    pulse_id: UUID = Field(foreign_key="pulses.pulse_id", index=True)

    index: UUID = Field(default_factory=uuid4, primary_key=True)


class PulseAttrsFloatRead(PulseAttrsReadBase):
    value: StrictFloat


class PulseAttrsFloatCreate(PulseAttrsCreateBase):
    value: StrictFloat
    data_type: AttrDataType = Field(default=AttrDataType.FLOAT.value)

    @classmethod
    def create_mock(
        cls: type[PulseAttrsFloatCreate],
        key: str = "mock_float_key",
        value: float = 42.0,
    ) -> PulseAttrsFloatCreate:
        return cls(key=key, value=value)

    def as_dict(self: Self) -> AttrDict:
        return {"key": self.key, "value": self.value, "data_type": self.data_type}


class PulseAttrsFloatFilter(PulseAttrsFilterBase):
    min_value: StrictFloat | StrictInt
    max_value: StrictFloat | StrictInt


class PulseAttrsDatetimeFilter(PulseAttrsFilterBase):
    min_value: datetime
    max_value: datetime


# Has to be defined after definition of both classes
TPulseAttrsCreate: TypeAlias = PulseAttrsStrCreate | PulseAttrsFloatCreate
TAttrReadDataType: TypeAlias = PulseAttrsStrRead | PulseAttrsFloatRead
TAttrFilterDataType: TypeAlias = (
    PulseAttrsStrFilter | PulseAttrsFloatFilter | PulseAttrsDatetimeFilter
)


class PulseAttrs(BaseModel):
    pulse_id: UUID
    pulse_attributes: list[TPulseAttrsCreate]


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

    index: UUID = Field(default_factory=uuid4, primary_key=True)
