from fastapi import Depends
from sqlalchemy import and_
from sqlmodel import Session, select

from api.database import get_session
from api.public.attrs.models import (
    KeyValuePair,
    PulseIntAttrs,
    PulseKeyRegistry,
    PulseStrAttrs,
)
from api.public.pulse.models import Pulse, PulseRead
from api.utils.exceptions import (
    AttrDataTypeExistsError,
    AttrDataTypeUnsupportedError,
    PulseNotFoundError,
)


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
) -> list[dict[str, str]]:
    """Get all the keys for a pulse with id pulse_id."""
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise PulseNotFoundError(pulse_id=pulse_id)

    statement = select([PulseStrAttrs.key, PulseStrAttrs.value]).where(
        PulseStrAttrs.pulse_id == pulse_id,
    )
    results = db.execute(statement).fetchall()

    return [{"key": row[0], "value": row[1]} for row in results]


def read_all_keys(
    db: Session = Depends(get_session),
) -> dict[str, str]:
    """Get all unique keys and their corresponding data type."""
    return {
        key[0]: key[1]
        for key in db.query(PulseKeyRegistry.key, PulseKeyRegistry.data_type).all()
    }


def read_all_values_on_key(
    key: str,
    db: Session = Depends(get_session),
) -> list[str] | list[int]:
    """Get all unique values associated with a key."""
    # Determine data type of key
    data_type = (
        db.query(PulseKeyRegistry.data_type)
        .filter(
            PulseKeyRegistry.key == key,
        )
        .scalar()
    )

    # I wish to change this, so all logic regarding data types is in one place.
    # This is to ensure that if I add a new data type, I don't have to change this here.
    # However, the interface is fine, so I'll leave it for now for quick PR draft.
    if data_type == "string":
        statement_str = (
            select(PulseStrAttrs.value).where(PulseStrAttrs.key == key).distinct()
        )
        return db.execute(statement_str).scalars().all()
    if data_type == "integer":
        statement_int = (
            select(PulseIntAttrs.value).where(PulseIntAttrs.key == key).distinct()
        )
        return db.execute(statement_int).scalars().all()
    raise AttrDataTypeUnsupportedError(data_type)


def filter_on_key_value_pairs(
    key_value_pairs: list[dict[str, str]],
    db: Session = Depends(get_session),
) -> list[int]:
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


def filter_on_kv_string(
    key_value_pair: dict[str, str],
    db: Session = Depends(get_session),
) -> list[int]:
    """Get all pulses that match this kv-pair, where value is string."""
    key = key_value_pair.get("key")
    value = key_value_pair.get("value")

    # Perform query for this key-value pair
    statement = select(PulseStrAttrs.pulse_id).where(
        and_(PulseStrAttrs.key == key, PulseStrAttrs.value == value),
    )
    results = db.execute(statement).fetchall()

    return [row[0] for row in results]


def filter_on_kv_int(
    key_value_pair: dict[str, int],
    db: Session = Depends(get_session),
) -> list[int]:
    """Get all pulses that match this kv-pair, where value is integer."""
    key = key_value_pair.get("key")
    value = key_value_pair.get("value")

    # Perform query for this key-value pair
    statement = select(PulseIntAttrs.pulse_id).where(
        and_(PulseIntAttrs.key == key, PulseIntAttrs.value == value),
    )
    results = db.execute(statement).fetchall()

    return [row[0] for row in results]
