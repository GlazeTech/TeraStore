from datetime import datetime
from enum import Enum, auto
from typing import TypeVar


class Lifespan(Enum):
    """Enum for the lifespan argument of create_app."""

    PROD = auto()
    DEV = auto()
    TEST = auto()


TPulseCols = TypeVar("TPulseCols", int, None, str, float, datetime)
