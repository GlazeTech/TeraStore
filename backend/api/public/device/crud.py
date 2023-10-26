from uuid import UUID

from fastapi import Depends
from sqlmodel import Session, select

from api.database import _get_session
from api.public.device.models import Device, DeviceCreate


def create_device(
    device: DeviceCreate,
    db: Session = Depends(_get_session),
) -> Device:
    """Create a new Device in the database.

    Args:
    ----
        device (DeviceCreate): The Device to create.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        The created Device including its DB ID.
    """
    device_to_db = Device.from_orm(device)
    db.add(device_to_db)
    db.commit()
    db.refresh(device_to_db)
    return device_to_db


def read_devices(
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(_get_session),
) -> list[Device]:
    """Read all Devices from the database.

    Args:
    ----
        offset (int, optional): The offset for the query. Defaults to 0.
        limit (int, optional): The limit for the query. Defaults to 20.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        A list of Devices.
    """
    return db.exec(select(Device).offset(offset).limit(limit)).all()


def read_device(device_id: UUID, db: Session = Depends(_get_session)) -> Device | None:
    """Read a single Pulse from the database.

    Args:
    ----
        device_id (UUID): The ID of the Device to read.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        The Device.
    """
    return db.get(Device, device_id)
