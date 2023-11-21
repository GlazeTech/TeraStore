from collections.abc import Sequence

from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.database import get_session
from api.public.attrs.crud import (
    filter_on_key_value_pairs,
    read_all_keys,
    read_all_values_on_key,
)
from api.public.attrs.models import (
    TAttrDataTypeList,
    TAttrFilterDataType,
)

router = APIRouter()


@router.get("/keys")
def get_all_keys(db: Session = Depends(get_session)) -> list[str]:
    return read_all_keys(db=db)


@router.get("/{key}/values")
def get_all_values_on_key(
    key: str,
    db: Session = Depends(get_session),
) -> TAttrDataTypeList:
    return read_all_values_on_key(key=key, db=db)


@router.post("/filter")
def filter_attrs(
    kv_pairs: Sequence[TAttrFilterDataType],
    db: Session = Depends(get_session),
) -> list[int]:
    return filter_on_key_value_pairs(kv_pairs, db)
