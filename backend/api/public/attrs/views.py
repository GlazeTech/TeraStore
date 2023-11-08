from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.database import get_session
from api.public.attrs.crud import (
    filter_on_key_value_pairs,
    read_all_keys,
    read_all_values_on_key,
)
from api.public.attrs.models import PulseIntAttrsFilter, PulseStrAttrsFilter

router = APIRouter()


@router.get("/keys")
def get_all_keys(db: Session = Depends(get_session)) -> dict[str, str]:
    return read_all_keys(db=db)


@router.get("/{key}/values")
def get_all_values_on_key(
    key: str,
    db: Session = Depends(get_session),
) -> list[str] | list[int] | None:
    try:
        return read_all_values_on_key(key=key, db=db)
    except ValueError:
        # It seems we cannot type annotate an empty list. Guido says no:
        # https://github.com/python/typing/issues/157
        # Or, they suggest you use list[object], but that doesn't satisfy Mypy.
        # We'll have to return a None instead.
        return None


@router.post("/filter")
def filter_attrs(
    key_value_pairs: list[PulseIntAttrsFilter | PulseStrAttrsFilter],
    db: Session = Depends(get_session),
) -> list[int]:
    """Filter pulses based on key-value pairs.

    Example usage:
    --------------
        curl -X 'POST' \
        'http://localhost:8000/attrs/filter' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '[
        {"key": "project", "value": "hempel", "data_type": "string"},
        {"key": "an_int", "min_value": "1", "max_value": "5", "data_type": "integer"}
        ]'
    """
    return filter_on_key_value_pairs(key_value_pairs, db)
