from fastapi import Depends
from sqlmodel import Session, select

from api.database import get_session
from api.public.attrs.models import (
    KeyValuePair,
    PulseIntAttrs,
    PulseIntAttrsFilter,
    PulseIntAttrsRead,
    PulseKeyRegistry,
    PulseStrAttrs,
    PulseStrAttrsFilter,
    PulseStrAttrsRead,
)
from api.public.pulse.models import Pulse, PulseRead
from api.utils.exceptions import (
    AttrDataTypeExistsError,
    AttrDataTypeUnsupportedError,
    AttrKeyNotFoundError,
    PulseNotFoundError,
)


def check_attr_data_type(
    key: str,
    db: Session = Depends(get_session),
) -> PulseKeyRegistry | None:
    """Check the data type of a key."""
    # Find the index in PulseKeyRegistry for this key
    statement = select(PulseKeyRegistry).where(PulseKeyRegistry.key == key)
    result = db.exec(statement).first()
    if not result:
        return None
    return result


def read_key_values(
    key: PulseKeyRegistry,
    db: Session = Depends(get_session),
) -> list[int] | list[str]:
    # I wish to change this, so all logic regarding data types is in one place.
    # This is to ensure that if I add a new data type, I don't have to change this here.
    # However, the interface is fine, so I'll leave it for now for quick PR draft.
    if key.data_type == "string":
        statement_str = (
            select(PulseStrAttrs.value).where(PulseStrAttrs.key == key.key).distinct()
        )
        return db.exec(statement_str).all()
    if key.data_type == "integer":
        statement_int = (
            select(PulseIntAttrs.value).where(PulseIntAttrs.key == key.key).distinct()
        )
        return db.exec(statement_int).all()
    raise AttrDataTypeUnsupportedError(key.data_type)


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

    existing_key = check_attr_data_type(key=kv_pair.key, db=db)

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
) -> list[PulseStrAttrsRead | PulseIntAttrsRead]:
    """Get all the keys for a pulse with id pulse_id."""
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise PulseNotFoundError(pulse_id=pulse_id)

    # Find all string attributes on pulse
    statement_str = select(PulseStrAttrs).where(
        PulseStrAttrs.pulse_id == pulse_id,
    )
    results_str = [
        PulseStrAttrsRead.from_orm(obj) for obj in db.exec(statement_str).all()
    ]

    # Find all integer attributes on pulse
    statement_int = select(PulseIntAttrs).where(
        PulseIntAttrs.pulse_id == pulse_id,
    )
    results_int = [
        PulseIntAttrsRead.from_orm(obj) for obj in db.exec(statement_int).all()
    ]

    # Combine the results
    return results_str + results_int


def read_all_keys(
    db: Session = Depends(get_session),
) -> list[dict[str, str]]:
    """Get all unique keys and their corresponding data type."""
    return [
        {"name": key[0], "data_type": key[1]}
        for key in db.query(PulseKeyRegistry.key, PulseKeyRegistry.data_type).all()
    ]


def read_all_values_on_key(
    key: str,
    db: Session = Depends(get_session),
) -> list[int] | list[str]:
    """Get all unique values associated with a key."""
    # Determine data type of key
    existing_key = check_attr_data_type(key=key, db=db)
    if not existing_key:
        raise AttrKeyNotFoundError(key=key)

    return read_key_values(key=existing_key, db=db)


def filter_on_key_value_pairs(
    key_value_pairs: list[PulseStrAttrsFilter | PulseIntAttrsFilter],
    db: Session = Depends(get_session),
) -> list[int]:
    """Get all pulses that match the key-value pairs."""
    # Initialize a list to hold pulse_ids for each condition
    pulse_ids_list: list[set[int]] = []

    # If no filters applied, select all pulses
    if len(key_value_pairs) == 0:
        statement = select(Pulse.pulse_id)
        pulses = db.exec(statement).all()
        return [pulse for pulse in pulses if pulse is not None]

    for kv in key_value_pairs:
        if isinstance(kv, PulseStrAttrsFilter):
            results = create_attr_str_filter_statement(kv, db=db)
        elif isinstance(kv, PulseIntAttrsFilter):
            results = create_attr_int_filter_statement(kv, db=db)
        else:
            raise AttrDataTypeUnsupportedError(kv.data_type)
        pulse_ids = set(results)
        pulse_ids_list.append(pulse_ids)

    # Find the intersection of all sets of pulse_ids
    common_pulse_ids = set.intersection(*pulse_ids_list)

    return list(common_pulse_ids)


def create_attr_str_filter_statement(
    kv_pair: PulseStrAttrsFilter,
    db: Session = Depends(get_session),
) -> list[int]:
    """Create a filter statement for a string attribute."""
    key = kv_pair.key
    value = kv_pair.value

    # Create statement for this key-value pair
    statement = (
        select(PulseStrAttrs.pulse_id)
        .where(PulseStrAttrs.key == key)
        .where(PulseStrAttrs.value == value)
    )
    return db.exec(statement).all()


def create_attr_int_filter_statement(
    kv_pair: PulseIntAttrsFilter,
    db: Session = Depends(get_session),
) -> list[int]:
    """Create a filter statement for an integer attribute."""
    key = kv_pair.key
    min_value = kv_pair.coaxed_min_value
    max_value = kv_pair.coaxed_max_value

    # Create statement for this key-value pair
    statement = (
        select(PulseIntAttrs.pulse_id)
        .where(PulseIntAttrs.key == key)
        .where(PulseIntAttrs.value >= min_value)
        .where(PulseIntAttrs.value <= max_value)
    )
    return db.exec(statement).all()
