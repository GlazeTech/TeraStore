from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from api.database import get_session
from api.public.attrs.models import PulseKeyRegistry, PulseStrAttrs
from api.public.pulse.models import Pulse


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
    pulse_str_attr = PulseStrAttrs(key=key, value=value, pulse_id=pulse_id)
    db.add(pulse_str_attr)

    db.commit()
    db.refresh(pulse)
    return pulse


def read_pulse_attr_keys(
    pulse_id: UUID,
    db: Session = Depends(get_session),
) -> list[str]:
    """Get all the keys for a pulse with id pulse_id."""
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pulse not found with id: {pulse_id}",
        )
    # Get all the keys for the pulse
    return [
        key[0]
        for key in db.query(PulseStrAttrs.key)
        .filter(PulseStrAttrs.pulse_id == pulse_id)
        .all()
    ]


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
