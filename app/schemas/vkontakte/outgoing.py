from typing import Optional, List

from pydantic import BaseModel, Field


class KeyboardAction(BaseModel):
    type: str = Field(...)
    label: Optional[str] = Field(None)
    payload: str = Field(...)


class KeyboardButton(BaseModel):
    action: KeyboardAction = Field(...)
    color: Optional[str] = Field(None)


class Keyboard(BaseModel):
    one_time: bool = Field(False)
    inline: bool = Field(False)
    buttons: List[List[KeyboardButton]] = Field(...)


class Message(BaseModel):
    user_id: int = Field(...)
    message: str = Field(...)
    keyboard: Optional[Keyboard] = Field(None)
    lat: Optional[float] = Field(None)
    long: Optional[float] = Field(None)
    attachment: Optional[str] = Field(None)
    template: Optional[dict] = Field(None)


class Element(BaseModel):
    title: str = Field(None)
    description: str = Field(None)
    photo_id: str = Field(None)
    buttons: List[KeyboardButton] = Field(None)
    action: dict = Field({"type": "open_photo"})


class Template(BaseModel):
    type: str = Field("carousel")
    elements: List[Element] = Field(...)
