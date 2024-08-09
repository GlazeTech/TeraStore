from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.database import get_session
from api.public.device.crud import (
    create_device,
    create_device_attr,
    delete_device_attr,
    read_device,
    read_devices,
)
from api.public.device.models import DeviceCreate, DeviceRead, TDeviceAttr

router = APIRouter()


@router.post("")
def create_a_device(
    device: DeviceCreate,
    db: Session = Depends(get_session),
) -> DeviceRead:
    return create_device(device=device, db=db)


@router.get("")
def get_devices(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    db: Session = Depends(get_session),
) -> list[DeviceRead]:
    return read_devices(offset=offset, limit=limit, db=db)


@router.get("/{device_serial_number}")
def get_device(
    device_serial_number: str, db: Session = Depends(get_session)
) -> DeviceRead:
    return read_device(device_serial_number=device_serial_number, db=db)


@router.post("/{device_serial_number}/attrs")
def add_attr(device_attr: TDeviceAttr, db: Session = Depends(get_session)) -> str:
    create_device_attr(device_attr=device_attr, db=db)
    return f"Key {device_attr.key} added to device {device_attr.serial_number}"


@router.delete("/{device_serial_number}/attrs/{attr_key}")
def delete_attr(
    device_serial_number: str, attr_key: str, db: Session = Depends(get_session)
) -> str:
    delete_device_attr(
        device_serial_number=device_serial_number, attr_key=attr_key, db=db
    )
    return f"Attribute {attr_key} deleted from device {device_serial_number}"
