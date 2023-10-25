import secrets
from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo


def generate_random_numbers(
    n: int,
    lower_bound: float,
    upper_bound: float,
) -> list[float]:
    """Generate list of n random integers between lower_bound and upper_bound.

    Args:
    ----
        n (int): The number of random integers to generate.
        lower_bound (int): The lower bound (inclusive) for the random integers.
        upper_bound (int): The upper bound (exclusive) for the random integers.

    Returns:
    -------
        A list of random integers.
    """
    return [secrets.SystemRandom().uniform(lower_bound, upper_bound) for _ in range(n)]


def generate_scaled_numbers(n: int, scale_factor: float) -> list[float]:
    """Generate a list of numbers from 0 to < n and multiply each by scale_factor.

    Args:
    ----
        n (int): The upper limit (exclusive) for the numbers.
        scale_factor (float): The factor to multiply each number with.

    Returns:
    -------
        A list of scaled numbers.
    """
    return [i * scale_factor for i in range(n)]


def generate_random_integration_time() -> int:
    """Generate a random integration time.

    Returns
    -------
        A random integration time.
    """
    return secrets.SystemRandom().randint(1, 100)


def get_now(timezone: str = "Europe/Copenhagen") -> datetime:
    """Get the current time with timezone.

    Args:
    ----
        timezone (str, optional): The timezone. Defaults to "Europe/Copenhagen".

    Returns:
    -------
        The current time with timezone.
    """
    return datetime.now(tz=ZoneInfo(timezone))


def create_mock_pulse(
    device_id: UUID,
    length: int = 600,
    timescale: float = 1e-10,
    amplitude: float = 100.0,
) -> dict[str, list[float] | int | datetime | UUID]:
    """Create a mock pulse for testing purposes.

    Args:
    ----
        device_id (UUID): The id of the device that created the pulse.
        length (int, optional): The length of the pulse. Defaults to 600.
        timescale (float, optional): The timescale of the pulse. Defaults to 1e-10.
        amplitude (float, optional): The amplitude of the pulse. Defaults to 100.0.

    Returns:
    -------
        A mock pulse.
    """
    return {
        "delays": generate_scaled_numbers(length, timescale),
        "signal": generate_random_numbers(length, -amplitude, amplitude),
        "integration_time": generate_random_integration_time(),
        "creation_time": get_now(),
        "device_id": device_id,
    }
