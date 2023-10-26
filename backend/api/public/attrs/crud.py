from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_
from sqlmodel import Session, select

from api.database import _get_session
from api.public.attrs.models import PulseKeyRegistry, PulseStrAttrs
from api.public.pulse.models import Pulse


def add_str_attr(
    pulse_id: UUID,
    key: str,
    value: str,
    db: Session = Depends(_get_session),
) -> Pulse | None:
    """Add a key-value pair to a pulse with id pulse_id.

    If the key does not exist, it will be added to the PulseKeyRegistry.

    Args:
    ----
        pulse_id (UUID): The id of the pulse.
        key (str): The key to add.
        value (str): The value to add.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        The updated Pulse.
    """
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        return None

    existing_key = (
        db.query(PulseKeyRegistry).filter(PulseKeyRegistry.key == key).first()
    )

    # If key doesn't exist, add it to PulseKeyRegistry
    if not existing_key:
        new_key = PulseKeyRegistry(key=key)
        db.add(new_key)

    # Now, add the new EAV string attribute
    pulse_str_attr = PulseStrAttrs(key=key, value=value, pulse_id=pulse_id)
    db.add(pulse_str_attr)

    db.commit()
    db.refresh(pulse)
    return pulse


def read_pulse_attrs(
    pulse_id: UUID,
    db: Session = Depends(_get_session),
) -> list[dict[str, str]] | None:
    """Get all the keys for a pulse with id pulse_id.

    Args:
    ----
        pulse_id (UUID): The id of the pulse.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        A list of dicts containing the key-value pairs.
    """
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        return None

    statement = select([PulseStrAttrs.key, PulseStrAttrs.value]).where(
        PulseStrAttrs.pulse_id == pulse_id,
    )
    results = db.execute(statement).fetchall()

    return [{"key": row[0], "value": row[1]} for row in results]


def read_all_keys(
    db: Session = Depends(_get_session),
) -> list[str]:
    """Get all unique keys.

    Args:
    ----
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        A list of keys.
    """
    return [key[0] for key in db.query(PulseKeyRegistry.key).all()]


def read_all_values_on_key(
    key: str,
    db: Session = Depends(_get_session),
) -> list[str]:
    """Get all unique values associated with a key.

    Args:
    ----
        key (str): The key to search for.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        A list of values associated with the key.
    """
    statement = select(PulseStrAttrs.value).where(PulseStrAttrs.key == key).distinct()
    return db.execute(statement).scalars().all()


def filter_on_key_value_pairs(
    key_value_pairs: list[dict[str, str]],
    db: Session = Depends(_get_session),
) -> list[UUID]:
    """Get all pulses that match the key-value pairs.

    Args:
    ----
        key_value_pairs (list[dict[str, str]]): The key-value pairs to filter on.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        A list of pulse_ids that match the key-value pairs.
    """
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
