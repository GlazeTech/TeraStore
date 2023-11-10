from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from api.database import get_session
from api.public.attrs.crud import (
    filter_on_key_value_pairs,
    read_all_keys,
    read_all_values_on_key,
)
from api.public.attrs.models import (
    PulseIntAttrsFilter,
    PulseStrAttrsFilter,
)
from api.utils.exceptions import AttrKeyNotFoundError

router = APIRouter()


@router.get("/keys")
def get_all_keys(db: Session = Depends(get_session)) -> list[dict[str, str]]:
    return read_all_keys(db=db)


@router.get("/{key}/values")
def get_all_values_on_key(
    key: str,
    db: Session = Depends(get_session),
) -> list[int] | list[str]:
    try:
        return read_all_values_on_key(key=key, db=db)
    except AttrKeyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


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
