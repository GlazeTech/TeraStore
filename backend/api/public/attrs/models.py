from __future__ import annotations

from typing import Any, Literal, Self, TypeVar

from pydantic import root_validator
from sqlmodel import Field, SQLModel

from api.utils.exceptions import AttrDataConversionError

PulseStrAttrsFilterConfig_T = TypeVar(
    "PulseStrAttrsFilterConfig_T",
    bound="PulseStrAttrsFilter.Config",
)

PulseIntAttrsFilterConfig_T = TypeVar(
    "PulseIntAttrsFilterConfig_T",
    bound="PulseIntAttrsFilter.Config",
)

PulseAttrsRead_T = TypeVar(
    "PulseAttrsRead_T",
    bound="PulseStrAttrsRead | PulseIntAttrsRead",
)


class PulseAttrsBase(SQLModel):
    key: str


class PulseStrAttrs(PulseAttrsBase, table=True):
    """The purpose of this class is to interact with the database."""

    __tablename__ = "pulse_str_attrs"

    value: str
    pulse_id: int = Field(foreign_key="pulses.pulse_id", index=True)
    index: int | None = Field(default=None, primary_key=True)


class PulseStrAttrsRead(PulseAttrsBase):
    value: str
    data_type: Literal["string"] = Field(default="string")


class PulseStrAttrsFilter(PulseAttrsBase):
    value: str
    data_type: Literal["string"] = Field(default="string")

    class Config:
        @classmethod
        def schema_extra(
            cls: type[PulseStrAttrsFilterConfig_T],
            schema: dict[str, Any],
            _model: type[PulseIntAttrsFilter],
        ) -> None:
            schema["example"] = {
                "key": "project",
                "value": "hempel",
                "data_type": "string",
            }


class PulseIntAttrs(PulseAttrsBase, table=True):
    """The purpose of this class is to interact with the database."""

    __tablename__ = "pulse_int_attrs"

    value: int
    pulse_id: int = Field(foreign_key="pulses.pulse_id", index=True)
    index: int | None = Field(default=None, primary_key=True)


class PulseIntAttrsRead(PulseAttrsBase):
    value: int
    data_type: Literal["integer"] = Field(default="integer")


class PulseIntAttrsFilter(PulseAttrsBase):
    min_value: int
    max_value: int
    data_type: Literal["integer"] = Field(default="integer")

    class Config:
        @classmethod
        def schema_extra(
            cls: type[PulseIntAttrsFilterConfig_T],
            schema: dict[str, Any],
            _model: type[PulseIntAttrsFilter],
        ) -> None:
            schema["example"] = {
                "key": "frequency",
                "min_value": 1,
                "max_value": 5,
                "data_type": "integer",
            }

    @root_validator()
    @classmethod
    def check_min_max(
        cls: type[PulseIntAttrsFilter],
        values: dict[str, str],
    ) -> dict[str, str]:
        """Validate, with Pydantic, that the min_value and max_value fields are okay."""
        min_value, max_value = values.get("min_value"), values.get("max_value")
        # We need to guard against None to satisfy Mypy.
        if min_value is None:
            error_message = "min_value must be set"
            raise ValueError(error_message)
        if max_value is None:
            error_message = "max_value must be set"
            raise ValueError(error_message)
        # Check if min_value and max_value can be coaxed to int.
        try:
            int(min_value)
        # If the conversion fails, raise a custom exception.
        except ValueError as e:
            raise AttrDataConversionError(min_value) from e
        try:
            int(max_value)
        # If the conversion fails, raise a custom exception.
        except ValueError as e:
            raise AttrDataConversionError(max_value) from e
        # Check if min_value is less than or equal to max_value.
        if int(min_value) > int(max_value):
            error_message = "min_value must be less than or equal to max_value"
            raise ValueError(error_message)
        return values

    @property
    def coaxed_min_value(self: Self) -> int:
        """Return the min_value as an int."""
        return int(self.min_value)

    @property
    def coaxed_max_value(self: Self) -> int:
        """Return the max_value as an int."""
        return int(self.max_value)


class PulseKeyRegistryBase(SQLModel):
    key: str
    data_type: str


class PulseKeyRegistry(PulseKeyRegistryBase, table=True):
    """Table model for Pulse EAV key registry."""

    __tablename__ = "pulse_key_registry"

    index: int | None = Field(default=None, primary_key=True)


class PulseKeyRegistryRead(PulseKeyRegistryBase):
    """Pydantic model for Pulse EAV key registry."""

    index: int
