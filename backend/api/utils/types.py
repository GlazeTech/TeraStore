from datetime import datetime
from enum import Enum, auto
from typing import TypeVar
from uuid import UUID


class Lifespan(Enum):
    """Enum for the lifespan argument of create_app."""

    PROD = auto()
    DEV = auto()
    TEST = auto()
    INTEGRATION_TEST = auto()


TPulseCols = TypeVar("TPulseCols", UUID, datetime, int, float, str)
