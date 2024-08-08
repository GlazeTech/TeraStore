from fastapi import Depends
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from api.database import get_session
from api.public.device.models import Device, DeviceCreate, DeviceRead
from api.utils.exceptions import DeviceExistsError, DeviceNotFoundError


def create_device(
    device: DeviceCreate | Device,
    db: Session = Depends(get_session),
) -> DeviceRead:
    device_to_db = Device.model_validate(device)
    db.add(device_to_db)
    try:
        db.commit()
    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            raise DeviceExistsError(device.serial_number) from e

    db.refresh(device_to_db)

    return DeviceRead.model_validate(device_to_db)


def read_devices(
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_session),
) -> list[DeviceRead]:
    devices = db.exec(select(Device).offset(offset).limit(limit)).all()
    return [DeviceRead.model_validate(device) for device in devices]


def read_device(
    device_serial_number: str, db: Session = Depends(get_session)
) -> DeviceRead:
    device = db.exec(
        select(Device).where(Device.serial_number == device_serial_number)
    ).first()
    if not device:
        raise DeviceNotFoundError(device_serial_number=device_serial_number)
    return DeviceRead.model_validate(device)
