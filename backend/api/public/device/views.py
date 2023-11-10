from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.database import get_session
from api.public.device.crud import create_device, read_device, read_devices
from api.public.device.models import DeviceCreate, DeviceRead

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


@router.get("/{device_id}")
def get_device(device_id: int, db: Session = Depends(get_session)) -> DeviceRead:
    return read_device(device_id=device_id, db=db)
