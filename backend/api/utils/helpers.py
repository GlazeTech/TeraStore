import secrets
from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from api.utils.exceptions import PulseColumnNonexistentError
from api.utils.types import TPulseCols


def generate_random_numbers(
    n: int,
    lower_bound: float,
    upper_bound: float,
) -> list[float]:
    """Generate list of n random integers between lower_bound and upper_bound."""
    return [secrets.SystemRandom().uniform(lower_bound, upper_bound) for _ in range(n)]


def generate_scaled_numbers(n: int, scale_factor: float) -> list[float]:
    """Generate a list of numbers from 0 to < n and multiply each by scale_factor."""
    return [i * scale_factor for i in range(n)]


def generate_random_integration_time() -> int:
    return secrets.SystemRandom().randint(1, 100)


def get_now(timezone: str = "Europe/Copenhagen") -> datetime:
    return datetime.now(tz=ZoneInfo(timezone))


def create_mock_pulse(
    device_id: int,
    length: int = 600,
    timescale: float = 1e-10,
    amplitude: float = 100.0,
) -> dict[str, list[float] | int | datetime]:
    return {
        "delays": generate_scaled_numbers(length, timescale),
        "signal": generate_random_numbers(length, -amplitude, amplitude),
        "integration_time_ms": generate_random_integration_time(),
        "creation_time": get_now(),
        "device_id": device_id,
    }


def extract_device_id_from_pgerror(pgerror: str) -> UUID:
    """Find a device_id in a PostgreSQL error message."""
    detail = pgerror.split("Key (device_id)=(")[1]
    uuid = detail.split(")")[0]
    if uuid:
        return UUID(uuid)
    error_str = "No device_id found in error message."
    raise ValueError(error_str)


def get_model_columns_from_names(
    wanted_columns: list[str],
    model: type[BaseModel],
) -> tuple[TPulseCols, ...]:
    # Maps a list of row names to the corresponding SQLModel attributes.
    try:
        fields: tuple[TPulseCols, ...] = tuple(
            [getattr(model, attr) for attr in wanted_columns],
        )

    # If the column doesn't exist, raise an error
    except AttributeError as e:
        raise PulseColumnNonexistentError(
            wanted=str(e),
            columns=list(model.model_json_schema()["properties"]),
        ) from e
    return fields
