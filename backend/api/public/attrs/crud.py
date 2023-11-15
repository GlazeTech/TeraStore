from collections.abc import Callable, Sequence

from fastapi import Depends
from sqlalchemy import union
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from api.database import get_session
from api.public.attrs.models import (
    AttrDataType,
    PulseAttrsCreateBase,
    PulseAttrsFilterBase,
    PulseAttrsFloat,
    PulseAttrsFloatFilter,
    PulseAttrsStr,
    PulseAttrsStrFilter,
    PulseKeyRegistry,
    attr_data_type_list,
    attr_filter_data_type,
    attr_read_data_type,
    get_pulse_attrs_class,
    get_pulse_attrs_read_class,
)
from api.public.pulse.models import Pulse, PulseRead
from api.utils.exceptions import (
    AttrDataTypeExistsError,
    AttrKeyDoesNotExistError,
    PulseNotFoundError,
)

FilterFunctionType = Callable[..., SelectOfScalar[int]]


def add_attr(
    pulse_id: int,
    kv_pair: PulseAttrsCreateBase,
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
) -> list[attr_read_data_type]:
    """Get all the keys for a pulse with id pulse_id."""
    pulse = db.get(Pulse, pulse_id)

    attrs_list = []

    if not pulse:
        raise PulseNotFoundError(pulse_id=pulse_id)

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
) -> attr_data_type_list:
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
    kv_pairs: Sequence[attr_filter_data_type],
    db: Session = Depends(get_session),
) -> list[int]:
    """Get all pulses that match the key-value pairs."""
    # Initialize a list to hold pulse_ids for each condition
    select_statements: list[SelectOfScalar[int]] = []

    # If no filters applied, select all pulses
    if len(kv_pairs) == 0:
        pulses = db.exec(select(Pulse.pulse_id)).all()
        if pulses[0] is None:
            return []

    for kv in kv_pairs:
        try:
            kv_data_type = db.exec(
                select(PulseKeyRegistry.data_type).filter(
                    PulseKeyRegistry.key == kv.key,
                ),
            ).one()
        except NoResultFound as e:
            raise AttrKeyDoesNotExistError(key=kv.key) from e
        select_statements.append(create_filter_query(kv, kv_data_type))

    combined_select = union(*select_statements)

    result = db.execute(combined_select).all()
    return [pulse_id["pulse_id"] for pulse_id in result]


def create_filter_query(
    kv_pair: PulseAttrsFilterBase,
    kv_data_type: str,
) -> SelectOfScalar[int]:
    if kv_data_type == AttrDataType.STRING.value:
        return create_attr_str_filter_query(PulseAttrsStrFilter(**kv_pair.dict()))
    if kv_data_type == AttrDataType.FLOAT.value:
        return create_attr_float_filter_query(PulseAttrsFloatFilter(**kv_pair.dict()))

    error_str = "kv_pair must be of type PulseAttrsStrFilter or PulseAttrsFloatFilter"
    raise TypeError(error_str)


def create_attr_str_filter_query(kv_pair: PulseAttrsStrFilter) -> SelectOfScalar[int]:
    return (
        select(PulseAttrsStr.pulse_id)
        .where(PulseAttrsStr.key == kv_pair.key)
        .where(PulseAttrsStr.value == kv_pair.value)
    )


def create_attr_float_filter_query(
    kv_pair: PulseAttrsFloatFilter,
) -> SelectOfScalar[int]:
    return (
        select(PulseAttrsFloat.pulse_id)
        .where(PulseAttrsFloat.key == kv_pair.key)
        .where(PulseAttrsFloat.value >= kv_pair.min_value)
        .where(PulseAttrsFloat.value <= kv_pair.max_value)
    )
