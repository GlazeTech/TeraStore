from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.database import get_session
from api.public.attrs.crud import add_attr, read_pulse_attrs
from api.public.attrs.models import PulseAttrsCreateBase, TAttrReadDataType
from api.public.pulse.crud import (
    create_pulses,
    read_pulse,
    read_pulses,
    read_pulses_with_ids,
)
from api.public.pulse.models import PulseCreate, PulseRead

router = APIRouter()


@router.post("/create")
def add_pulses(
    pulses: list[PulseCreate],
    db: Session = Depends(get_session),
) -> list[UUID]:
    return create_pulses(pulses=pulses, db=db)


@router.get("")
def get_pulses(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    db: Session = Depends(get_session),
) -> list[PulseRead]:
    return read_pulses(offset=offset, limit=limit, db=db)


@router.post("/get")
def get_pulses_from_ids(
    ids: list[UUID],
    db: Session = Depends(get_session),
) -> list[PulseRead]:
    return read_pulses_with_ids(ids, db=db)


@router.get("/{pulse_id}")
def get_pulse(pulse_id: UUID, db: Session = Depends(get_session)) -> PulseRead:
    return read_pulse(pulse_id=pulse_id, db=db)


@router.put("/{pulse_id}/attrs")
def add_kv_pair(
    pulse_id: UUID,
    kv_pair: PulseAttrsCreateBase,
    db: Session = Depends(get_session),
) -> str:
    add_attr(kv_pair=kv_pair, pulse_id=pulse_id, db=db)
    return f"Key {kv_pair.key} added to pulse {pulse_id}"


@router.get("/{pulse_id}/attrs")
def get_pulse_keys(
    pulse_id: UUID,
    db: Session = Depends(get_session),
) -> list[TAttrReadDataType]:
    return read_pulse_attrs(pulse_id=pulse_id, db=db)
