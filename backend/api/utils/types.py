from enum import Enum


class WithLifespan(Enum):
    """Enum for the lifespan argument of create_app."""

    TRUE = True
    FALSE = False
