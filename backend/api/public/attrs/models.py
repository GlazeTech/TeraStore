from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Self, TypeVar

from pydantic import BaseModel, root_validator
from sqlmodel import Field, SQLModel

from api.utils.exceptions import AttrDataConversionError, AttrDataTypeUnsupportedError

PulseStrAttrsFilterConfig_T = TypeVar(
    "PulseStrAttrsFilterConfig_T",
    bound="PulseStrAttrsFilter.Config",
)

PulseIntAttrsFilterConfig_T = TypeVar(
    "PulseIntAttrsFilterConfig_T",
    bound="PulseIntAttrsFilter.Config",
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
        if not min_value:
            error_message = "min_value must be set"
            raise ValueError(error_message)
        if not max_value:
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


class PulseKeyRegistry(SQLModel, table=True):
    """Table model for Pulse EAV key registry."""

    __tablename__ = "pulse_key_registry"

    index: int | None = Field(default=None, primary_key=True)
    key: str = Field(index=True)
    data_type: str


class AllowedAttrDataType(Enum):
    STRING = "string"
    INTEGER = "integer"


class KeyValuePair(BaseModel):
    key: str
    value: str
    data_type: str

    @root_validator()
    @classmethod
    def check_data_type(
        cls: type[KeyValuePair],
        values: dict[str, str],
    ) -> dict[str, str]:
        """Validate, with Pydantic, that the data_type field is okay."""
        value, data_type = values.get("value"), values.get("data_type")
        # We need to guard against None to satisfy Mypy.
        if not value:
            error_message = "value must be set"
            raise ValueError(error_message)
        if not data_type:
            error_message = "data_type must be set"
            raise ValueError(error_message)
        # Check if data_type is allowed by AllowedAttrDataType enum.
        if data_type not in [member.value for member in AllowedAttrDataType]:
            raise AttrDataTypeUnsupportedError(data_type)
        # Value should be string. We know it is, because that's how it comes in.
        if data_type == AllowedAttrDataType.STRING.value:
            pass
        # Value should be integer. We need to coax it, and handle if it can't be.
        if data_type == AllowedAttrDataType.INTEGER.value:
            try:
                int(value)
            # If the conversion fails, raise a custom exception.
            except ValueError as e:
                raise AttrDataConversionError(data_type) from e
        return values

    def data_model_class(
        self: Self,
        pulse_id: int,
    ) -> PulseStrAttrs | PulseIntAttrs:
        """Return the data model class based on the data_type.

        This is to minimize where in the code we must make changes for new data types.

        """
        if self.data_type == AllowedAttrDataType.STRING.value:
            return PulseStrAttrs(
                key=self.key,
                value=self.value,
                pulse_id=pulse_id,
            )
        if self.data_type == AllowedAttrDataType.INTEGER.value:
            # Here we know that self.value safely can be coaxed to int.
            return PulseIntAttrs(
                key=self.key,
                value=int(self.value),
                pulse_id=pulse_id,
            )
        raise AttrDataTypeUnsupportedError(self.data_type)
