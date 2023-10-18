from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from api.database import get_session
from api.public.pulse.models import Pulse, PulseCreate, PulseKeyRegistry, PulseStrAttrs


def create_pulse(pulse: PulseCreate, db: Session = Depends(get_session)) -> Pulse:
    """Create a new Pulse in the database.

    Args:
    ----
        pulse (PulseCreate): The Pulse to create.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        The created Pulse including its DB ID.
    """
    pulse_to_db = Pulse.from_orm(pulse)
    db.add(pulse_to_db)
    db.commit()
    db.refresh(pulse_to_db)
    return pulse_to_db


def read_pulses(
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_session),
) -> list[Pulse]:
    """Read all Pulses from the database.

    Args:
    ----
        offset (int, optional): The offset for the query. Defaults to 0.
        limit (int, optional): The limit for the query. Defaults to 20.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        A list of Pulses.
    """
    return db.exec(select(Pulse).offset(offset).limit(limit)).all()


def read_pulse(pulse_id: UUID, db: Session = Depends(get_session)) -> Pulse:
    """Read a single Pulse from the database.

    Args:
    ----
        pulse_id (UUID): The ID of the Pulse to read.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Raises:
    ------
        HTTPException: If no Pulse is found with the given ID.

    Returns:
    -------
        The Pulse with the given ID.
    """
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pulse not found with id: {pulse_id}",
        )
    return pulse


def add_str_attr(
    pulse_id: UUID,
    key: str,
    value: str,
    db: Session = Depends(get_session),
) -> Pulse:
    """Add a key-value pair to a pulse with id pulse_id."""
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pulse not found with id: {pulse_id}",
        )
    # Check if the key exists in PulseKeyRegistry
    existing_key = (
        db.query(PulseKeyRegistry).filter(PulseKeyRegistry.key == key).first()
    )

    # If key doesn't exist, add it to PulseKeyRegistry
    if not existing_key:
        new_key = PulseKeyRegistry(key=key)
        db.add(new_key)

    # Now, add the new EAV string attribute
    pulse_eav_string = PulseStrAttrs(key=key, value=value, pulse_id=pulse_id)
    db.add(pulse_eav_string)

    db.commit()
    db.refresh(pulse)
    return pulse
