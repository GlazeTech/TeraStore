from collections.abc import Sequence
from uuid import UUID

from fastapi import Depends
from sqlmodel import Session, col, select

from api.database import get_session
from api.public.pulse.models import Pulse
from api.utils.exceptions import PulseNotFoundError


def assert_pulses_exist(
    pulse_ids: Sequence[UUID],
    db: Session = Depends(get_session),
) -> None:
    """Check that all pulse IDs exist in the database.

    Raises a PulseNotFoundError if not.
    """
    existing_pulses = db.exec(
        select(Pulse.pulse_id).filter(col(Pulse.pulse_id).in_(pulse_ids)),
    ).all()
    if len(existing_pulses) != len(pulse_ids):
        raise PulseNotFoundError(
            pulse_id=[
                pulse_id for pulse_id in pulse_ids if pulse_id not in existing_pulses
            ],
        )
