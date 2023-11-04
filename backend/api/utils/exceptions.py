from __future__ import annotations

from typing import Self


class AttrDataTypeExistsError(Exception):
    """Exception raised when the data type of an attribute already exists."""

    def __init__(self: Self, key: str, data_type: str) -> None:
        self.key = key
        self.data_type = data_type
        super().__init__(f"Key {key} already exists with data type {data_type}.")


class AttrDataTypeUnsupportedError(Exception):
    """Exception raised when the data type of an attribute is not supported."""

    def __init__(self: Self, data_type: str) -> None:
        self.data_type = data_type
        super().__init__(f"Data type {data_type} not supported.")


class AttrDataConversionError(Exception):
    """Exception raised when the data type of an attribute is not supported."""

    def __init__(self: Self, data_type: str) -> None:
        self.data_type = data_type
        super().__init__(f"Value cannot be cast to {data_type}.")
