from enum import Enum, auto


class Lifespan(Enum):
    """Enum for the lifespan argument of create_app."""

    PROD = auto()
    DEV = auto()
    TEST = auto()
