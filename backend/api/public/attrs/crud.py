from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_
from sqlmodel import Session, select

from api.database import get_session
from api.public.attrs.models import (
    KeyValuePair,
    PulseKeyRegistry,
    PulseStrAttrs,
)
from api.public.pulse.models import Pulse, PulseRead
from api.utils.exceptions import AttrDataTypeExistsError, PulseNotFoundError


def create_attr(
    pulse_id: int,
    kv_pair: KeyValuePair,
    db: Session = Depends(get_session),
) -> Pulse:
    """Create a new EAV attribute for a pulse with id pulse_id."""
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise PulseNotFoundError(pulse_id=pulse_id)

    pulse_read = PulseRead.from_orm(pulse)

    # Check if given key exists.
    existing_key = (
        db.query(PulseKeyRegistry).filter(PulseKeyRegistry.key == kv_pair.key).first()
    )

    # Check if key already exists and if so, check if data type matches
    if existing_key and existing_key.data_type != kv_pair.data_type:
        raise AttrDataTypeExistsError(key=kv_pair.key, data_type=kv_pair.data_type)

    # If key doesn't exist, add it to PulseKeyRegistry
    if not existing_key:
        new_key = PulseKeyRegistry.from_orm(
            PulseKeyRegistry(key=kv_pair.key, data_type=kv_pair.data_type),
        )
        db.add(new_key)
        db.commit()

    # Add the new EAV attribute
    pulse_attr = kv_pair.data_model_class(pulse_read.pulse_id)

    db.add(pulse_attr)

    db.commit()
    db.refresh(pulse)
    return Pulse.from_orm(pulse)


def read_pulse_attrs(
    pulse_id: int,
    db: Session = Depends(get_session),
) -> list[dict[str, str]] | None:
    """Get all the keys for a pulse with id pulse_id."""
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        return None

    statement = select([PulseStrAttrs.key, PulseStrAttrs.value]).where(
        PulseStrAttrs.pulse_id == pulse_id,
    )
    results = db.execute(statement).fetchall()

    return [{"key": row[0], "value": row[1]} for row in results]


def read_all_keys(
    db: Session = Depends(get_session),
) -> list[str]:
    """Get all unique keys."""
    return [key[0] for key in db.query(PulseKeyRegistry.key).all()]


def read_all_values_on_key(
    key: str,
    db: Session = Depends(get_session),
) -> list[str]:
    """Get all unique values associated with a key."""
    statement = select(PulseStrAttrs.value).where(PulseStrAttrs.key == key).distinct()
    return db.execute(statement).scalars().all()


def filter_on_key_value_pairs(
    key_value_pairs: list[dict[str, str]],
    db: Session = Depends(get_session),
) -> list[UUID]:
    """Get all pulses that match the key-value pairs."""
    # Initialize a list to hold pulse_ids for each condition
    pulse_ids_list = []

    # If no filters applied, select all pulses
    if len(key_value_pairs) == 0:
        return db.execute(select(Pulse.pulse_id)).scalars().all()

    for kv in key_value_pairs:
        key = kv.get("key")
        value = kv.get("value")

        # Perform query for this key-value pair
        statement = select(PulseStrAttrs.pulse_id).where(
            and_(PulseStrAttrs.key == key, PulseStrAttrs.value == value),
        )
        results = db.execute(statement).fetchall()

        # Convert results to set of pulse_ids and add to list
        pulse_ids = {row[0] for row in results}
        pulse_ids_list.append(pulse_ids)

    # Find the intersection of all sets of pulse_ids
    common_pulse_ids = set.intersection(*pulse_ids_list)

    return list(common_pulse_ids)
