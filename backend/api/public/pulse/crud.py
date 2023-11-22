from fastapi import Depends
from psycopg2.errors import ForeignKeyViolation
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from api.database import get_session
from api.public.pulse.models import Pulse, PulseCreate, PulseRead, TemporaryPulseIdTable
from api.utils.exceptions import (
    DeviceNotFoundError,
    PulseNotFoundError,
)
from api.utils.helpers import extract_device_id_from_pgerror


def create_pulses(
    pulses: list[PulseCreate],
    db: Session = Depends(get_session),
) -> list[int]:
    pulses_to_db = [Pulse.from_orm(pulse) for pulse in pulses]
    for pulse_to_db in pulses_to_db:
        db.add(pulse_to_db)
    try:
        db.commit()
    except IntegrityError as e:
        if isinstance(e.orig, ForeignKeyViolation):
            if e.orig.pgerror is None:
                raise
            device_id = extract_device_id_from_pgerror(e.orig.pgerror)
            raise DeviceNotFoundError(device_id=device_id) from e
    for pulse_to_db in pulses_to_db:
        db.refresh(pulse_to_db)
    return [PulseRead.from_orm(pulse_to_db).pulse_id for pulse_to_db in pulses_to_db]


def read_pulses(
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_session),
) -> list[PulseRead]:
    """Get all pulses in the database."""
    pulses = db.exec(select(Pulse).offset(offset).limit(limit)).all()
    return [PulseRead.from_orm(pulse) for pulse in pulses]


def read_pulses_with_ids(
    ids: list[int],
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


def read_pulse(pulse_id: int, db: Session = Depends(get_session)) -> PulseRead:
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise PulseNotFoundError(pulse_id=pulse_id)
    return PulseRead.from_orm(pulse)
