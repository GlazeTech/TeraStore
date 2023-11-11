from __future__ import annotations

from typing import Self


class PulseNotFoundError(Exception):
    """Exception raised when the data type of an attribute is not supported."""

    def __init__(self: Self, pulse_id: int) -> None:
        self.pulse_id = pulse_id
        super().__init__(f"Pulse not found with id: {pulse_id}")


class DeviceNotFoundError(Exception):
    """Exception raised when the data type of an attribute is not supported."""

    def __init__(self: Self, device_id: int) -> None:
        self.device_id = device_id
        super().__init__(f"Device not found with id: {device_id}")
