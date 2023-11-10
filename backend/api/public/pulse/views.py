from fastapi import APIRouter, Depends, HTTPException, Query, status
from psycopg2.errors import ForeignKeyViolation
from sqlalchemy.exc import DBAPIError
from sqlmodel import Session

from api.database import get_session
from api.public.attrs.crud import create_attr, read_pulse_attrs
from api.public.attrs.models import PulseIntAttrsRead, PulseStrAttrsRead
from api.public.pulse.crud import (
    create_pulse,
    read_pulse,
    read_pulses,
    read_pulses_with_ids,
)
from api.public.pulse.models import Pulse, PulseCreate, PulseRead

router = APIRouter()


@router.post("/create", response_model=PulseRead)
def create_a_pulse(
    pulse: PulseCreate,
    db: Session = Depends(get_session),
) -> PulseRead:
    try:
        return create_pulse(pulse=pulse, db=db)
    except DBAPIError as e:
        if isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device not found with id: {pulse.device_id}",
            ) from e
        raise


@router.get("", response_model=list[PulseRead])
def get_pulses(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    db: Session = Depends(get_session),
) -> list[Pulse]:
    return read_pulses(offset=offset, limit=limit, db=db)


@router.post("/get", response_model=list[PulseRead])
def get_pulses_from_ids(
    ids: list[int],
    db: Session = Depends(get_session),
) -> list[PulseRead]:
    return read_pulses_with_ids(ids, db=db)


@router.get("/{pulse_id}", response_model=PulseRead)
def get_pulse(pulse_id: int, db: Session = Depends(get_session)) -> PulseRead:
    return read_pulse(pulse_id=pulse_id, db=db)


@router.put("/{pulse_id}/attrs", response_model=PulseRead)
def add_attr(
    pulse_id: int,
    kv_pair: PulseStrAttrsRead | PulseIntAttrsRead,
    db: Session = Depends(get_session),
) -> Pulse:
    return create_attr(
        pulse_id=pulse_id,
        kv_pair=kv_pair,
        db=db,
    )


@router.get("/{pulse_id}/attrs")
def get_pulse_keys(
    pulse_id: int,
    db: Session = Depends(get_session),
) -> list[PulseStrAttrsRead | PulseIntAttrsRead]:
    return read_pulse_attrs(pulse_id=pulse_id, db=db)
