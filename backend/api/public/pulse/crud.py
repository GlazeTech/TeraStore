from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from api.database import get_session
from api.public.pulse.models import Pulse, PulseCreate


def create_pulse(pulse: PulseCreate, db: Session = Depends(get_session)) -> PulseCreate:
    """Create a new Pulse in the database."""
    pulse_to_db = PulseCreate.from_orm(pulse)
    db.add(pulse_to_db)
    db.commit()
    db.refresh(pulse_to_db)
    return pulse_to_db


def read_pulses(
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_session),
) -> list[Pulse]:
    """Read all Pulses from the database."""
    return db.exec(select(Pulse).offset(offset).limit(limit)).all()


def read_pulse(pulse_id: UUID, db: Session = Depends(get_session)) -> Pulse:
    """Read a single Pulse from the database."""
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pulse not found with id: {pulse_id}",
        )
    return pulse
