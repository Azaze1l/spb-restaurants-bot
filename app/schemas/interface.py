import datetime
from typing import Optional, List
from fastapi import status
from fastapi import HTTPException
from pydantic import BaseModel, Field, validator


class InterfaceButtonObject(BaseModel):
    id: str = Field(..., title="Object's id in mongo")
    object: str = Field(..., title="Object's name")
    type: str = Field(..., title="Object's type (keyboard, button, reply)")
    text: Optional[str] = Field(..., title="Object's set text")
    title: str = Field(..., title="Description of interface object")
    platform: str = Field(..., title="Object's platform (vk, tg)")
    created_at: datetime.datetime = Field(..., title="Datetime of creating object")
    updated_at: Optional[datetime.datetime] = Field(
        ..., title="Datetime of updating object"
    )


class InterfaceObjectInfo(BaseModel):
    id: str = Field(..., title="Object's id in mongo")
    object: str = Field(..., title="Object's name")
    type: str = Field(..., title="Object's type (keyboard, button, reply)")
    text: str = Field(None, title="Object's set text")
    title: str = Field(..., title="Description of interface object")
    platform: str = Field(..., title="Object's platform (vk, tg)")
    created_at: datetime.datetime = Field(..., title="Datetime of creating object")
    updated_at: Optional[datetime.datetime] = Field(
        ..., title="Datetime of updating object"
    )
    buttons: List[InterfaceButtonObject] = Field(
        None, title="List of buttons (if type is keyboard)"
    )


class DefaultResponse(BaseModel):
    status: str = Field(..., title="Status of operation (ok or failed)")


class InterfaceObjectUpdate(BaseModel):
    text: Optional[str] = Field(None, title="Object's text to update")
    platform: Optional[str] = Field(
        None, title="Objects's platform (not necessary for ObjectId definition)"
    )

    @validator("platform")
    def platform_match(cls, platform):
        if platform not in ("tg", "vk"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platform must be 'tg' or 'vk'",
            )
        return platform
