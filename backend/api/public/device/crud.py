from uuid import UUID

from fastapi import Depends
from sqlmodel import Session, select

from api.database import get_session
from api.public.device.models import Device, DeviceCreate, DeviceRead


def create_device(
    device: DeviceCreate,
    db: Session = Depends(get_session),
) -> DeviceRead:
    device_to_db = Device.from_orm(device)
    db.add(device_to_db)
    db.commit()
    db.refresh(device_to_db)
    return DeviceRead.from_orm(device_to_db)


def read_devices(
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_session),
) -> list[Device]:
    return db.exec(select(Device).offset(offset).limit(limit)).all()


def read_device(device_id: UUID, db: Session = Depends(get_session)) -> Device | None:
    return db.get(Device, device_id)
