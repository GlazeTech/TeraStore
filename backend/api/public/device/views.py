from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from api.database import _get_session
from api.public.device.crud import create_device, read_device, read_devices
from api.public.device.models import Device, DeviceCreate, DeviceRead

router = APIRouter()


@router.post("", response_model=DeviceRead)
def create_a_device(
    device: DeviceCreate,
    db: Session = Depends(_get_session),
) -> Device:
    """Create a new Device in the database from the API.

    Args:
    ----
        device (DeviceCreate): The Device to create.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        The created Device including its DB ID.
    """
    return create_device(device=device, db=db)


@router.get("", response_model=list[DeviceRead])
def get_devices(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    db: Session = Depends(_get_session),
) -> list[Device]:
    """Read all Devices from the database via the API.

    Args:
    ----
        offset (int, optional): The offset for the query. Defaults to 0.
        limit (int, optional): The limit for the query. Defaults to 20.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
    -------
        A list of Devices.
    """
    return read_devices(offset=offset, limit=limit, db=db)


@router.get("/{device_id}", response_model=DeviceRead)
def get_device(device_id: UUID, db: Session = Depends(_get_session)) -> Device:
    """Read a single Device from the database via the API.

    Args:
    ----
        device_id (UUID): The ID of the Device to read.
        db (Session, optional): The database session. Defaults to Depends(get_session).

    Raises:
    ------
        HTTPException: If the Device is not found.

    Returns:
    -------
        The Device with the given ID.
    """
    device = read_device(device_id=device_id, db=db)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device not found with id: {device_id}",
        )

    return device
