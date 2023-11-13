from typing import cast

from fastapi import Depends
from pydantic.types import StrictStr
from sqlmodel import Session, select

from api.database import get_session
from api.public.attrs.models import PulseAttrsStr, PulseAttrsStrRead, PulseKeyRegistry
from api.public.pulse.models import Pulse, PulseRead
from api.utils.exceptions import PulseNotFoundError


def add_str_attr(
    pulse_id: int,
    key: str,
    value: str,
    db: Session = Depends(get_session),
) -> PulseRead:
    """Add a key-value pair to a pulse with id pulse_id."""
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise PulseNotFoundError(pulse_id=pulse_id)

    existing_key = (
        db.query(PulseKeyRegistry).filter(PulseKeyRegistry.key == key).first()
    )

    # If key doesn't exist, add it to PulseKeyRegistry
    if not existing_key:
        new_key = PulseKeyRegistry(key=key)
        db.add(new_key)

    # Now, add the new EAV string attribute
    pulse_str_attr = PulseAttrsStr(key=key, value=value, pulse_id=pulse_id)
    db.add(pulse_str_attr)

    db.commit()
    db.refresh(pulse)
    return PulseRead.from_orm(pulse)


def read_pulse_attrs(
    pulse_id: int,
    db: Session = Depends(get_session),
) -> list[PulseAttrsStrRead]:
    """Get all the keys for a pulse with id pulse_id."""
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise PulseNotFoundError(pulse_id=pulse_id)

    statement = select(PulseAttrsStr).where(
        PulseAttrsStr.pulse_id == pulse_id,
    )
    attrs = db.exec(statement).all()
    return [PulseAttrsStrRead.from_orm(attr) for attr in attrs]


def read_all_keys(
    db: Session = Depends(get_session),
) -> list[str]:
    """Get all unique keys."""
    statement = select(PulseKeyRegistry.key).distinct()
    return db.exec(statement).all()


def read_all_values_on_key(
    key: str,
    db: Session = Depends(get_session),
) -> list[StrictStr]:
    """Get all unique values associated with a key."""
    statement = select(PulseAttrsStr.value).where(PulseAttrsStr.key == key).distinct()
    return db.exec(statement).all()


def filter_on_key_value_pairs(
    kv_pairs: list[PulseAttrsStrRead],
    db: Session = Depends(get_session),
) -> list[int]:
    """Get all pulses that match the key-value pairs."""
    # Initialize a list to hold pulse_ids for each condition
    pulse_ids_list: list[set[int]] = []

    # If no filters applied, select all pulses
    if len(kv_pairs) == 0:
        pulses = db.exec(select(Pulse.pulse_id)).all()
        if pulses[0] is None:
            return []
        return cast(list[int], pulses)

    for kv in kv_pairs:
        # Perform query for this key-value pair
        statement = (
            select(PulseAttrsStr.pulse_id)
            .where(PulseAttrsStr.key == kv.key)
            .where(PulseAttrsStr.value == kv.value)
        )
        pulse_ids = db.exec(statement).all()
        pulse_ids_list.append(set(pulse_ids))

    # Find the intersection of all sets of pulse_ids
    common_pulse_ids: set[int] = set.intersection(*pulse_ids_list)

    return list(common_pulse_ids)
