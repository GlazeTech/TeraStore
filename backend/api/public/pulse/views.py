from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from psycopg2.errors import ForeignKeyViolation
from sqlalchemy.exc import DBAPIError
from sqlmodel import Session

from api.database import _get_session
from api.public.attrs.crud import add_str_attr, read_pulse_attrs
from api.public.pulse.crud import (
    create_pulse,
    read_pulse,
    read_pulses,
)
from api.public.pulse.models import Pulse, PulseCreate, PulseRead

router = APIRouter()


@router.post("", response_model=PulseRead)
def create_a_pulse(
    pulse: PulseCreate,
    db: Session = Depends(_get_session),
) -> Pulse:
    """Create a new Pulse in the database from the API.

    Args:
    ----
        pulse (PulseCreate): The Pulse to create.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Raises:
    ------
        HTTPException: If no Device is found with the given ID.

    Returns:
    -------
        The created Pulse including its DB ID.
    """
    try:
        return create_pulse(pulse=pulse, db=db)
    except DBAPIError as e:
        if isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device not found with id: {pulse.device_id}",
            ) from e
        raise


@router.get("", response_model=list[PulseRead])
def get_pulses(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    db: Session = Depends(_get_session),
) -> list[Pulse]:
    """Read all Pulses from the database via the API.

    Args:
    ----
        offset (int, optional): The offset for the query. Defaults to 0.
        limit (int, optional): The limit for the query. Defaults to 20.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        A list of Pulses.
    """
    return read_pulses(offset=offset, limit=limit, db=db)


@router.get("/{pulse_id}", response_model=PulseRead)
def get_pulse(pulse_id: UUID, db: Session = Depends(_get_session)) -> Pulse:
    """Read a single Pulse from the database via the API.

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
    pulse = read_pulse(pulse_id=pulse_id, db=db)
    if not pulse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pulse not found with id: {pulse_id}",
        )
    return pulse


@router.put("/{pulse_id}/attrs", response_model=PulseRead)
def add_kv_str(
    pulse_id: UUID,
    key: str,
    value: str,
    db: Session = Depends(_get_session),
) -> Pulse:
    """Add a key-value pair to a Pulse with pulse_id.

    Args:
    ----
        pulse_id (UUID): The ID of the Pulse to add the key-value pair to.
        key (str): The key to add.
        value (str): The value to add.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Raises:
    ------
        HTTPException: If no Pulse is found with the given ID.

    Returns:
    -------
        The Pulse with the given ID.
    """
    pulse = add_str_attr(key=key, value=value, pulse_id=pulse_id, db=db)
    if not pulse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pulse not found with id: {pulse_id}",
        )
    return pulse


@router.get("/{pulse_id}/attrs")
def get_pulse_keys(
    pulse_id: UUID,
    db: Session = Depends(_get_session),
) -> list[dict[str, str]]:
    """Get all keys associated with a Pulse.

    Args:
    ----
        pulse_id (UUID): The ID of the Pulse to get the keys from.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Raises:
    ------
        HTTPException: If no Pulse is found with the given ID.

    Returns:
    -------
        A list of dicts containing the keys and values.
    """
    pulse_attrs = read_pulse_attrs(pulse_id=pulse_id, db=db)
    if not pulse_attrs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pulse not found with id: {pulse_id}",
        )
    return pulse_attrs
