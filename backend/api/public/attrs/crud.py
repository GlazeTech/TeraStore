from collections.abc import Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy.engine.row import Row
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, intersect, select
from sqlmodel.sql.expression import SelectOfScalar

from api.database import get_session
from api.public.attrs.models import (
    AttrDataType,
    PulseAttrs,
    PulseAttrsCreateBase,
    PulseAttrsDatetimeFilter,
    PulseAttrsFilterBase,
    PulseAttrsFloat,
    PulseAttrsFloatFilter,
    PulseAttrsStr,
    PulseAttrsStrFilter,
    PulseKeyRegistry,
    TAttrDataTypeList,
    TAttrFilterDataType,
    TAttrReadDataType,
    get_pulse_attrs_class,
    get_pulse_attrs_read_class,
)
from api.public.pulse.helpers import assert_pulses_exist
from api.public.pulse.models import Pulse
from api.utils.exceptions import (
    AttrDataTypeExistsError,
    AttrKeyDoesNotExistError,
    PulseNotFoundError,
)
from api.utils.helpers import get_model_columns_from_names
from api.utils.types import TPulseCols


def add_attrs(
    pulses_attrs: Sequence[PulseAttrs],
    db: Session = Depends(get_session),
) -> None:
    """Bulk inserts all the attributes for a list of pulses."""
    # Find all unique keys and data types
    unique_keys_set = set()
    for pulse_attrs in pulses_attrs:
        for attrs in pulse_attrs.pulse_attributes:
            unique_keys_set.add((attrs.key, attrs.data_type))

    unique_keys: list[str] = [e[0] for e in list(unique_keys_set)]
    unique_keys_datatypes: list[AttrDataType] = [e[1] for e in list(unique_keys_set)]

    # Raise an error if the data type of an existing key is wrong
    known_keys = db.exec(
        select(PulseKeyRegistry).where(col(PulseKeyRegistry.key).in_(unique_keys)),
    ).all()
    for known_key in known_keys:
        new_key_type = unique_keys_datatypes[unique_keys.index(known_key.key)]
        if known_key.data_type != new_key_type:
            raise AttrDataTypeExistsError(
                key=known_key.key,
                existing_data_type=known_key.data_type,
                incoming_data_type=new_key_type,
            )

    # If some keys doesn't exist, add them to PulseKeyRegistry
    new_keys: set[str] = set(unique_keys) - {key.key for key in known_keys}
    for new_key in new_keys:
        datatype = unique_keys_datatypes[unique_keys.index(new_key)]
        db.add(PulseKeyRegistry(key=new_key, data_type=datatype))

    # Add the new EAV attributes
    for pulse_attrs in pulses_attrs:
        for attrs in pulse_attrs.pulse_attributes:
            attr_cls = get_pulse_attrs_class(attrs.data_type)
            db.add(attr_cls(pulse_id=pulse_attrs.pulse_id, **attrs.dict()))

    # Finally, commit all changes
    db.commit()


def add_attr(
    pulse_id: UUID,
    kv_pair: PulseAttrsCreateBase,
    db: Session = Depends(get_session),
) -> None:
    """Add a key-value pair to a pulse with id pulse_id."""
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise PulseNotFoundError(pulse_id=pulse_id)

    existing_key = db.exec(
        select(PulseKeyRegistry).where(PulseKeyRegistry.key == kv_pair.key),
    ).first()
    # Check if key already exists and if so, check if data type matches
    if existing_key and existing_key.data_type != kv_pair.data_type:
        raise AttrDataTypeExistsError(
            key=kv_pair.key,
            existing_data_type=existing_key.data_type,
            incoming_data_type=kv_pair.data_type.value,
        )

    # If key doesn't exist, add it to PulseKeyRegistry
    if not existing_key:
        new_key = PulseKeyRegistry(key=kv_pair.key, data_type=kv_pair.data_type)
        db.add(new_key)

    # Now, add the new EAV attribute
    pulse_attrs_class = get_pulse_attrs_class(AttrDataType(kv_pair.data_type))

    db.add(pulse_attrs_class(**kv_pair.dict(), pulse_id=pulse_id))
    db.commit()


def read_pulse_attrs(
    pulse_ids: Sequence[UUID],
    db: Session = Depends(get_session),
    *,
    check_pulses_exist: bool = True,
) -> dict[UUID, list[TAttrReadDataType]]:
    """Get all the keys for a pulse with id pulse_id."""
    if check_pulses_exist:
        assert_pulses_exist(pulse_ids=pulse_ids, db=db)

    results: dict[UUID, list[TAttrReadDataType]] = {
        pulse_id: [] for pulse_id in pulse_ids
    }

    # Read attrs for all data types
    for data_type in AttrDataType:
        attrs_class = get_pulse_attrs_class(data_type)
        attrs_read_class = get_pulse_attrs_read_class(data_type)
        loaded_attrs = db.exec(
            select(attrs_class).where(col(attrs_class.pulse_id).in_(pulse_ids)),
        ).all()

        # Add loaded attrs to results
        for pulse_id in pulse_ids:
            for attr in loaded_attrs:
                # Mypy thinks attr is PulseAttrsBase, which is wrong
                if attr.pulse_id == pulse_id:  # type: ignore[attr-defined]
                    results[pulse_id].append(
                        attrs_read_class.model_validate(attr),
                    )

    return results


def read_all_keys(
    db: Session = Depends(get_session),
) -> Sequence[tuple[str, str]]:
    """Get all unique keys."""
    statement = select(PulseKeyRegistry.key, PulseKeyRegistry.data_type).distinct()
    return db.exec(statement).all()


def read_all_values_on_key(
    key: str,
    db: Session = Depends(get_session),
) -> TAttrDataTypeList:
    """Get all unique values associated with a key."""
    # Get key if it exists from PulseKeyRegistry
    existing_key = db.exec(
        select(PulseKeyRegistry).where(PulseKeyRegistry.key == key),
    ).first()
    if not existing_key:
        raise AttrKeyDoesNotExistError(key=key)

    attrs_class = get_pulse_attrs_class(AttrDataType(existing_key.data_type))
    return db.exec(
        select(attrs_class.value).where(attrs_class.key == key).distinct(),
    ).all()


def filter_on_key_value_pairs(
    kv_pairs: Sequence[TAttrFilterDataType],
    wanted_columns: list[str],
    db: Session = Depends(get_session),
) -> Sequence[tuple[TPulseCols, ...]]:
    """Get all pulses that match the key-value pairs."""
    # Initialize a list to hold pulse_ids for each condition
    select_statements: list[SelectOfScalar[UUID]] = []

    # If no filters applied, select all pulses
    if len(kv_pairs) == 0:
        # Using exec(..), if pulse_fields is a tuple with a single attribute,
        # a list of integers is returned.
        # If it contains more than one attribute, a list of Row objects is returned,
        # and the type annotation is not correct. Hence, use SQLAlchemy method.
        pulses = db.execute(
            select(*get_model_columns_from_names(wanted_columns, Pulse)),
        ).all()
        if not pulses:
            return []
        if isinstance(pulses[0], Row):
            return [tuple(e) for e in pulses]
        raise TypeError

    for kv in kv_pairs:
        # Because creation_time is in the pulses table, we need to handle it separately
        # As we do not allow datetime attrs, we can simply check the instance type
        if isinstance(kv, PulseAttrsDatetimeFilter):
            select_statements.append(create_attr_creation_time_filter_query(kv))
            continue
        try:
            kv_data_type = db.exec(
                select(PulseKeyRegistry.data_type).where(
                    PulseKeyRegistry.key == kv.key,
                ),
            ).one()
        except NoResultFound as e:
            raise AttrKeyDoesNotExistError(key=kv.key) from e
        select_statements.append(create_filter_query(kv, kv_data_type))

    combined_select = intersect(*select_statements)

    # We need to use SQLAlchemy's execute method here because we need to
    # run a compound select statement.
    # Additionally, if only the pulse_id is requested, we don't need to join
    if wanted_columns == ["pulse_id"]:
        r = db.execute(combined_select).unique().all()
    else:
        sub_query = combined_select.subquery("sub_query")
        # Use SQLAlchemy's execute method, because SQLModel has wrong types and doesn't
        # know .unique() and .all()
        r = (
            db.execute(
                select(*get_model_columns_from_names(wanted_columns, Pulse)).join(
                    sub_query,
                    col(Pulse.pulse_id) == sub_query.c.pulse_id,
                ),
            )
            .unique()
            .all()
        )

    return [tuple(e) for e in r]


def create_filter_query(
    kv_pair: PulseAttrsFilterBase,
    kv_data_type: str,
) -> SelectOfScalar[UUID]:
    if kv_data_type == AttrDataType.STRING.value:
        return create_attr_str_filter_query(PulseAttrsStrFilter(**kv_pair.dict()))
    if kv_data_type == AttrDataType.FLOAT.value:
        return create_attr_float_filter_query(PulseAttrsFloatFilter(**kv_pair.dict()))

    error_str = "kv_pair must be of type PulseAttrsStrFilter or PulseAttrsFloatFilter"
    raise TypeError(error_str)


def create_attr_creation_time_filter_query(
    kv_pair: PulseAttrsDatetimeFilter,
) -> SelectOfScalar[UUID]:
    return (
        select(Pulse.pulse_id)
        .where(Pulse.creation_time >= kv_pair.min_value)
        .where(Pulse.creation_time <= kv_pair.max_value)
    )


def create_attr_str_filter_query(kv_pair: PulseAttrsStrFilter) -> SelectOfScalar[UUID]:
    return (
        select(PulseAttrsStr.pulse_id)
        .where(PulseAttrsStr.key == kv_pair.key)
        .where(PulseAttrsStr.value == kv_pair.value)
    )


def create_attr_float_filter_query(
    kv_pair: PulseAttrsFloatFilter,
) -> SelectOfScalar[UUID]:
    return (
        select(PulseAttrsFloat.pulse_id)
        .where(PulseAttrsFloat.key == kv_pair.key)
        .where(PulseAttrsFloat.value >= kv_pair.min_value)
        .where(PulseAttrsFloat.value <= kv_pair.max_value)
    )
