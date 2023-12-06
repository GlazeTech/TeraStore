from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import Depends
from psycopg2.errors import ForeignKeyViolation
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from api.database import get_session
from api.public.attrs.crud import add_attrs, read_pulse_attrs
from api.public.pulse.helpers import assert_pulses_exist
from api.public.pulse.models import (
    AnnotatedPulseRead,
    Pulse,
    PulseCreate,
    PulseRead,
    TemporaryPulseIdTable,
)
from api.utils.exceptions import (
    AttrDataTypeExistsError,
    DeviceNotFoundError,
    PulseNotFoundError,
)
from api.utils.helpers import extract_device_id_from_pgerror

if TYPE_CHECKING:
    from api.public.attrs.models import PulseAttrs


def create_pulses(
    pulses: list[PulseCreate],
    db: Session = Depends(get_session),
) -> list[UUID]:
    pulses_to_db: list[Pulse] = []
    pulses_attrs_to_db: list[PulseAttrs] = []
    for pulse in pulses:
        pulse_to_db, pulse_attrs_to_db = pulse.create_pulse()
        pulses_to_db.append(pulse_to_db)
        pulses_attrs_to_db.append(pulse_attrs_to_db)

    # We get the IDs here, because if we do it later,
    # SQLModel will verify the ID with a call to the database.
    ids = [pulse.pulse_id for pulse in pulses_to_db]

    for pulse_to_db in pulses_to_db:
        db.add(pulse_to_db)
    try:
        # SQLModel does a bulk insert here
        db.commit()
    except IntegrityError as e:
        if isinstance(e.orig, ForeignKeyViolation):
            if e.orig.pgerror is None:
                raise
            device_id = extract_device_id_from_pgerror(e.orig.pgerror)
            raise DeviceNotFoundError(device_id=device_id) from e

    try:
        add_attrs(pulses_attrs=pulses_attrs_to_db, db=db)
    except AttrDataTypeExistsError:
        # If we failed to add all pulse attributes, reset the database
        pulses_to_delete = db.exec(
            select(Pulse).filter(col(Pulse.pulse_id).in_(ids)),
        ).all()
        for p in pulses_to_delete:
            db.delete(p)
        db.commit()
        raise

    return ids


def read_pulses(
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_session),
) -> list[PulseRead]:
    """Get all pulses in the database."""
    pulses = db.exec(select(Pulse).offset(offset).limit(limit)).all()
    return [PulseRead.model_validate(pulse) for pulse in pulses]


def read_pulses_with_ids(
    ids: list[UUID],
    db: Session = Depends(get_session),
) -> list[AnnotatedPulseRead]:
    # Assert wanted pulses exist
    assert_pulses_exist(pulse_ids=ids, db=db)

    # Save wanted ID's in a temporary table
    db.bulk_save_objects([TemporaryPulseIdTable(pulse_id=idx) for idx in ids])
    db.commit()

    # Select all pulses whose ID is in the temporary table
    pulses = db.exec(
        select(Pulse).join(
            TemporaryPulseIdTable,
            col(TemporaryPulseIdTable.pulse_id) == col(Pulse.pulse_id),
            isouter=False,
        ),
    ).all()

    # Find all attributes for the selected pulses
    pulse_attrs = read_pulse_attrs(pulse_ids=ids, db=db, check_pulses_exist=False)

    # Delete the entries from the temporary table again
    db.query(TemporaryPulseIdTable).delete()
    db.commit()
    return [
        AnnotatedPulseRead.new(pulse=pulse, attrs=pulse_attrs[pulse.pulse_id])
        for pulse in pulses
    ]


def read_pulse(pulse_id: UUID, db: Session = Depends(get_session)) -> PulseRead:
    pulse = db.get(Pulse, pulse_id)
    if not pulse:
        raise PulseNotFoundError(pulse_id=pulse_id)
    return PulseRead.model_validate(pulse)
