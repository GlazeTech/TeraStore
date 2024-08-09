from typing import cast

from fastapi import Depends
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import Session, col, select

from api.database import get_session
from api.public.device.models import (
    Device,
    DeviceCreate,
    DeviceRead,
    TDeviceAttr,
    device_attrs_tables,
)
from api.utils.exceptions import DeviceExistsError, DeviceNotFoundError


def create_device(
    device: DeviceCreate,
    db: Session = Depends(get_session),
) -> DeviceRead:
    device_to_db = Device.model_validate(device)
    db.add(device_to_db)
    try:
        db.commit()
    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            raise DeviceExistsError(device.serial_number) from e

    if device.attrs is None:
        db.refresh(device_to_db)
        return DeviceRead.new(device_to_db)

    for table in device_attrs_tables():
        attrs = [attr for attr in device.attrs if attr.table is table]
        db.add_all([table.model_validate(attr) for attr in attrs])

    db.commit()
    db.refresh(device_to_db)
    return DeviceRead.new(device_to_db)


def read_devices(
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_session),
) -> list[DeviceRead]:
    devices = db.exec(select(Device).offset(offset).limit(limit)).all()
    device_attrs = _read_device_attrs([device.serial_number for device in devices], db)

    return [
        DeviceRead.new(
            device=device,
            attributes=[
                a for a in device_attrs if a.serial_number == device.serial_number
            ],
        )
        for device in devices
    ]


def read_device(
    device_serial_number: str, db: Session = Depends(get_session)
) -> DeviceRead:
    device = db.exec(
        select(Device).where(Device.serial_number == device_serial_number)
    ).first()
    if not device:
        raise DeviceNotFoundError(device_serial_number=device_serial_number)

    device_attrs = _read_device_attrs([device_serial_number], db)
    return DeviceRead.new(device, device_attrs)


def create_device_attr(
    device_attr: TDeviceAttr,
    db: Session = Depends(get_session),
) -> None:
    db.add(device_attr.table.model_validate(device_attr))
    db.commit()


def delete_device_attr(
    device_serial_number: str, attr_key: str, db: Session = Depends(get_session)
) -> None:
    for table in device_attrs_tables():
        try:
            instance = db.exec(
                select(table)
                .where(col(table.serial_number) == device_serial_number)
                .where(col(table.key) == attr_key)
            ).one()
            db.delete(instance)
            db.commit()
        except NoResultFound:
            continue
        else:
            return

    msg = f"Attribute {attr_key} on device {device_serial_number} not found"
    raise NoResultFound(msg)


def _read_device_attrs(
    device_serial_numbers: list[str], db: Session
) -> list[TDeviceAttr]:
    all_attrs: list[TDeviceAttr] = []
    for table in device_attrs_tables():
        attrs = db.exec(
            select(table).where(col(table.serial_number).in_(device_serial_numbers))
        ).all()
        all_attrs.extend(cast(list[TDeviceAttr], attrs))
    return all_attrs
