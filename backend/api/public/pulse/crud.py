from fastapi import Depends
from sqlmodel import Session, select

from api.database import get_session
from api.public.pulse.models import Pulse, PulseCreate, PulseRead


def create_pulse(pulse: PulseCreate, db: Session = Depends(get_session)) -> PulseRead:
    pulse_to_db = Pulse.from_orm(pulse)

    db.add(pulse_to_db)
    db.commit()
    db.refresh(pulse_to_db)
    return PulseRead.from_orm(pulse_to_db)


def read_pulses(
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_session),
) -> list[Pulse]:
    """Get all pulses in the database."""
    return db.exec(select(Pulse).offset(offset).limit(limit)).all()


def read_pulse(pulse_id: int, db: Session = Depends(get_session)) -> Pulse | None:
    return db.get(Pulse, pulse_id)
