from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.database import get_session
from api.public.attrs.crud import (
    filter_on_key_value_pairs,
    read_all_keys,
    read_all_values_on_key,
)

router = APIRouter()


@router.get("/keys")
def get_all_keys(db: Session = Depends(get_session)) -> list[str]:
    """Get all keys.

    Args:
    ----
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        A list of keys.
    """
    return read_all_keys(db=db)


@router.get("/{key}/values")
def get_all_values_on_key(key: str, db: Session = Depends(get_session)) -> list[str]:
    """Get all values associated with a key.

    Args:
    ----
        key (str): The key to search for.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        A list of values associated with the key.
    """
    return read_all_values_on_key(key=key, db=db)


@router.post("/filter")
def filter_attrs(
    key_value_pairs: list[dict[str, str]],
    db: Session = Depends(get_session),
) -> list[UUID]:
    """Filter pulses based on key-value pairs.

    Example usage:
    --------------
        curl -X 'POST' \
        'http://localhost:8000/attrs/filter' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '[
        {"key": "angle", "value": "17"},
        {"key": "substrate", "value": "plastic"}
        ]'

    Args:
    ----
        key_value_pairs (list[dict[str, str]]): A list of dicts containing kv pairs.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        A list of pulse ids.
    """
    return filter_on_key_value_pairs(key_value_pairs, db)
