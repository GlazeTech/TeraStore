from __future__ import annotations

from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from uuid import UUID


class PulseNotFoundError(Exception):
    """Exception raised when the data type of an attribute is not supported."""

    def __init__(self: Self, pulse_id: UUID | list[UUID]) -> None:
        self.pulse_id = pulse_id
        super().__init__(f"Pulse not found with id: {pulse_id}")


class PulseColumnNonexistentError(Exception):
    """Exception raised when a user requests a nonexistent pulse column."""

    def __init__(self: Self, wanted: str, columns: list[str]) -> None:
        self.wanted = wanted
        self.available_columns = columns
        super().__init__(
            f"Pulse column not found: {wanted}. Available columns are: {columns}",
        )


class DeviceNotFoundError(Exception):
    """Exception raised when the data type of an attribute is not supported."""

    def __init__(self: Self, device_id: UUID) -> None:
        self.device_id = device_id
        super().__init__(f"Device not found with id: {device_id}")


class AttrDataTypeExistsError(Exception):
    """Exception raised when the data type of an attribute already exists."""

    def __init__(
        self: Self,
        key: str,
        existing_data_type: str,
        incoming_data_type: str,
    ) -> None:
        self.key = key
        self.existing_data_type = existing_data_type
        self.incoming_data_type = incoming_data_type
        super().__init__(
            f"Key {key} already exists with data type '{existing_data_type}'. "
            f"You gave '{incoming_data_type}'.",
        )


class AttrKeyDoesNotExistError(Exception):
    """Exception raised when a key does not exist."""

    def __init__(
        self: Self,
        key: str,
    ) -> None:
        self.key = key
        super().__init__(
            f"Key {key} does not exist.",
        )


class AttrDataTypeDoesNotExistError(Exception):
    """Exception raised when a data type does not exist."""

    def __init__(
        self: Self,
        data_type: str,
    ) -> None:
        self.data_type = data_type
        super().__init__(
            f"Data type {data_type} does not exist.",
        )


class EmailOrPasswordIncorrectError(Exception):
    """Exception raised when a username or password is incorrect."""

    def __init__(
        self: Self,
    ) -> None:
        super().__init__(
            "Email or password is incorrect.",
        )


class UserAlreadyExistsError(Exception):
    """Exception raised when a username already exists."""

    def __init__(
        self: Self,
        email: str,
    ) -> None:
        self.email = email
        super().__init__(
            f"Email {email} already exists.",
        )


class CredentialsIncorrectError(Exception):
    """Exception raised when credentials are incorrect."""

    def __init__(
        self: Self,
    ) -> None:
        super().__init__(
            "Could not validate credentials.",
        )
