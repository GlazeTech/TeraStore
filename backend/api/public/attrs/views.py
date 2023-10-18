from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.database import get_session
from api.public.attrs.crud import (
    add_str_attr,
    read_all_keys,
    read_all_values_on_key,
    read_pulse_attr_keys,
)
from api.public.pulse.models import Pulse, PulseRead

router = APIRouter()


@router.get("")
def get_all_keys(db: Session = Depends(get_session)) -> list[str]:
    """Get all keys associated with a Pulse."""
    return read_all_keys(db=db)


@router.put("/{pulse_id}", response_model=PulseRead)
def add_kv_str(
    pulse_id: UUID,
    key: str,
    value: str,
    db: Session = Depends(get_session),
) -> Pulse:
    """Add a key-value pair to a Pulse with pulse_id."""
    return add_str_attr(key=key, value=value, pulse_id=pulse_id, db=db)


@router.get("/{pulse_id}")
def get_pulse_keys(pulse_id: UUID, db: Session = Depends(get_session)) -> list[str]:
    """Get all keys associated with a Pulse."""
    return read_pulse_attr_keys(pulse_id=pulse_id, db=db)


@router.get("/{key}")
def get_all_values_on_key(key: str, db: Session = Depends(get_session)) -> list[str]:
    """Get all values associated with a key."""
    return read_all_values_on_key(key=key, db=db)
