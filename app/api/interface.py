from typing import Optional, Union, List
from fastapi import Body, HTTPException, status, APIRouter, Depends
import bson
from app.helpers.deps import get_current_user
from app.schemas.interface import (
    InterfaceObjectInfo,
    DefaultResponse,
    InterfaceObjectUpdate,
)
from app.db.interface_objects import InterfaceObjects, _fill_id_without_underscore
from app.db import get_db

interface_objects_router = APIRouter()


@interface_objects_router.post("/{object_id_or_name}", response_model=DefaultResponse)
async def update_interface_objects_text(
    object_id_or_name: str,
    update_data: InterfaceObjectUpdate,
    user=Depends(get_current_user),
):
    db = await get_db()
    try:
        object_id = bson.ObjectId(object_id_or_name)
        elem = await InterfaceObjects.update_interface_object_by_id(
            db, object_id, update_data.text
        )
        if not elem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no such modifiable item with this id",
            )
        return {"status": "ok"}
    except bson.errors.InvalidId:
        object_name = object_id_or_name
        if update_data.platform is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Field 'platform' is required",
            )
        if object_name.endswith("keyboard"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This operation is not allowed with keyboards",
            )
        elem = await InterfaceObjects.update_interface_object_by_name(
            db, object_name, update_data.platform, update_data.text
        )
        if not elem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no such modifiable item with this name",
            )
        return {"status": "ok"}


@interface_objects_router.get(
    "/{object_id_or_name}",
    response_model=Union[List[InterfaceObjectInfo], InterfaceObjectInfo],
    response_model_exclude_unset=True,
)
async def get_object_by_id_or_name(
    object_id_or_name: str,
    platform: Optional[str] = None,
    user=Depends(get_current_user),
):
    db = await get_db()
    try:
        object_id = bson.ObjectId(object_id_or_name)
        object_info = await InterfaceObjects.get_object_by_id(db, object_id)
        if not object_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no such modifiable item with this id",
            )
        return _fill_id_without_underscore(object_info)

    except bson.errors.InvalidId:
        object_name = object_id_or_name
        objects_info = await InterfaceObjects.get_interface_object(
            db, object_name, platform
        )
        if not objects_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no such modifiable item with this name",
            )
        return _fill_id_without_underscore(objects_info)


@interface_objects_router.get("/")
async def get_objects_by_type_or_platform(
    object_type: Optional[str] = None,
    platform: Optional[str] = None,
    user=Depends(get_current_user),
):
    db = await get_db()
    objects_info = await InterfaceObjects.get_element_by_type_and_platform(
        db, object_type, platform
    )
    if not objects_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There is no such modifiable item with this type or platform",
        )
    return _fill_id_without_underscore(objects_info)
