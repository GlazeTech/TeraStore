from collections.abc import Callable

from fastapi import Depends
from pydantic.types import StrictFloat, StrictStr
from sqlmodel import Session, select

from api.database import get_session
from api.public.attrs.models import (
    AttrDataType,
    PulseAttrsFloat,
    PulseAttrsFloatCreate,
    PulseAttrsFloatFilter,
    PulseAttrsFloatRead,
    PulseAttrsStr,
    PulseAttrsStrCreate,
    PulseAttrsStrFilter,
    PulseAttrsStrRead,
    PulseKeyRegistry,
    get_pulse_attrs_class,
    get_pulse_attrs_read_class,
)
from api.public.pulse.models import Pulse, PulseRead
from api.utils.exceptions import (
    AttrDataTypeExistsError,
    AttrKeyDoesNotExistError,
    PulseNotFoundError,
)

FilterFunctionType = Callable[..., list[int]]


def add_attr(
    pulse_id: int,
    kv_pair: PulseAttrsStrCreate | PulseAttrsFloatCreate,
    db: Session = Depends(get_session),
) -> PulseRead:
    """Add a key-value pair to a pulse with id pulse_id."""
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise PulseNotFoundError(pulse_id=pulse_id)

    existing_key = (
        db.query(PulseKeyRegistry).filter(PulseKeyRegistry.key == kv_pair.key).first()
    )
    # Check if key already exists and if so, check if data type matches
    if existing_key and existing_key.data_type != kv_pair.data_type:
        raise AttrDataTypeExistsError(
            key=kv_pair.key,
            existing_data_type=existing_key.data_type,
            incoming_data_type=kv_pair.data_type,
        )

    # If key doesn't exist, add it to PulseKeyRegistry
    if not existing_key:
        new_key = PulseKeyRegistry(key=kv_pair.key, data_type=kv_pair.data_type)
        db.add(new_key)

    # Now, add the new EAV attribute
    pulse_attrs_class = get_pulse_attrs_class(AttrDataType(kv_pair.data_type))

    db.add(pulse_attrs_class(**kv_pair.dict(), pulse_id=pulse_id))
    db.commit()
    db.refresh(pulse)
    return PulseRead.from_orm(pulse)


def read_pulse_attrs(
    pulse_id: int,
    db: Session = Depends(get_session),
) -> list[PulseAttrsStrRead | PulseAttrsFloatRead]:
    """Get all the keys for a pulse with id pulse_id."""
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise PulseNotFoundError(pulse_id=pulse_id)

    attrs_list = []

    for data_type in AttrDataType:
        attrs_class = get_pulse_attrs_class(data_type)
        attrs_read_class = get_pulse_attrs_read_class(data_type)
        statement = select(attrs_class).where(attrs_class.pulse_id == pulse_id)
        attrs = [attrs_read_class.from_orm(obj) for obj in db.exec(statement).all()]
        attrs_list += attrs

    return attrs_list


def read_all_keys(
    db: Session = Depends(get_session),
) -> list[str]:
    """Get all unique keys."""
    statement = select(PulseKeyRegistry.key).distinct()
    return db.exec(statement).all()


def read_all_values_on_key(
    key: str,
    db: Session = Depends(get_session),
) -> list[StrictStr] | list[StrictFloat]:
    """Get all unique values associated with a key."""
    # Get key if it exists from PulseKeyRegistry
    existing_key = (
        db.query(PulseKeyRegistry).filter(PulseKeyRegistry.key == key).first()
    )
    if not existing_key:
        raise AttrKeyDoesNotExistError(key=key)

    attrs_class = get_pulse_attrs_class(AttrDataType(existing_key.data_type))
    statement = select(attrs_class.value).where(attrs_class.key == key).distinct()
    return db.exec(statement).all()


def filter_on_key_value_pairs(
    kv_pairs: list[PulseAttrsStrFilter | PulseAttrsFloatFilter],
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

    for kv in kv_pairs:
        filter_function = get_attr_filter_function(kv)
        pulse_ids = filter_function(kv, db)
        pulse_ids_list.append(set(pulse_ids))

    # Find the intersection of all sets of pulse_ids
    common_pulse_ids: set[int] = set.intersection(*pulse_ids_list)

    return list(common_pulse_ids)


def get_attr_filter_function(
    kv_pair: PulseAttrsStrFilter | PulseAttrsFloatFilter,
) -> FilterFunctionType:
    if isinstance(kv_pair, PulseAttrsStrFilter):
        return filter_attr_str
    if isinstance(kv_pair, PulseAttrsFloatFilter):
        return filter_attr_float

    error_str = "kv_pair must be of type PulseAttrsStrFilter or PulseAttrsFloatFilter"
    raise TypeError(error_str)


def filter_attr_str(
    kv_pair: PulseAttrsStrFilter,
    db: Session = Depends(get_session),
) -> list[int]:
    """Get all pulses that match the key-value pair."""
    statement = (
        select(PulseAttrsStr.pulse_id)
        .where(PulseAttrsStr.key == kv_pair.key)
        .where(PulseAttrsStr.value == kv_pair.value)
    )
    return db.exec(statement).all()


def filter_attr_float(
    kv_pair: PulseAttrsFloatFilter,
    db: Session = Depends(get_session),
) -> list[int]:
    """Get all pulses that match the key-value pair."""
    statement = (
        select(PulseAttrsFloat.pulse_id)
        .where(PulseAttrsFloat.key == kv_pair.key)
        .where(PulseAttrsFloat.value >= kv_pair.min_value)
        .where(PulseAttrsFloat.value <= kv_pair.max_value)
    )
    return db.exec(statement).all()
