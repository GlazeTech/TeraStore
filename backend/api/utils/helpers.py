import secrets
from datetime import datetime
from zoneinfo import ZoneInfo


def generate_random_numbers(
    n: int,
    lower_bound: int,
    upper_bound: int,
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
