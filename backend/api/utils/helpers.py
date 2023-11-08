import secrets
from datetime import datetime
from zoneinfo import ZoneInfo


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
        "integration_time": generate_random_integration_time(),
        "creation_time": get_now(),
        "device_id": device_id,
    }
