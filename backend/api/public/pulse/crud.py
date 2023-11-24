from uuid import UUID

from fastapi import Depends
from sqlmodel import Session, select

from api.database import get_session
from api.public.pulse.models import Pulse, PulseCreate, PulseRead, TemporaryPulseIdTable
from api.utils.exceptions import PulseNotFoundError


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
) -> list[PulseRead]:
    """Get all pulses in the database."""
    pulses = db.exec(select(Pulse).offset(offset).limit(limit)).all()
    return [PulseRead.from_orm(pulse) for pulse in pulses]


def read_pulses_with_ids(
    ids: list[UUID],
    db: Session = Depends(get_session),
) -> list[PulseRead]:
    # Save wanted ID's in a temporary table
    db.bulk_save_objects([TemporaryPulseIdTable(pulse_id=idx) for idx in ids])
    db.commit()

    # Select all pulses whose ID is in the temporary table
    pulses = db.exec(
        select(Pulse).join(
            TemporaryPulseIdTable,
            TemporaryPulseIdTable.pulse_id == Pulse.pulse_id,  # type: ignore[arg-type]
            isouter=False,
        ),
    ).all()

    # Delete the entries from the temporary table again
    db.query(TemporaryPulseIdTable).delete()
    db.commit()
    return [PulseRead.from_orm(pulse) for pulse in pulses]


def read_pulse(pulse_id: UUID, db: Session = Depends(get_session)) -> PulseRead:
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise PulseNotFoundError(pulse_id=pulse_id)
    return PulseRead.from_orm(pulse)
