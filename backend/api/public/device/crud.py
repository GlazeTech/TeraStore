from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from api.database import get_session
from api.public.device.models import Device, DeviceCreate


def create_device(
    device: DeviceCreate,
    db: Session = Depends(get_session),
) -> DeviceCreate:
    """Create a new Device in the database."""
    device_to_db = DeviceCreate.from_orm(device)
    db.add(device_to_db)
    db.commit()
    db.refresh(device_to_db)
    return device_to_db


def read_devices(
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_session),
) -> list[Device]:
    """Read all Devices from the database."""
    return db.exec(select(Device).offset(offset).limit(limit)).all()


def read_device(device_id: UUID, db: Session = Depends(get_session)) -> Device:
    """Read a single Pulse from the database."""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device not found with id: {device_id}",
        )
    return device
