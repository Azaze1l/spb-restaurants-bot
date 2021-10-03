from typing import Optional, List

from pydantic import BaseModel, Field


class ClientInfo(BaseModel):
    button_actions: List[str] = Field(...)
    carousel: bool = Field(...)
    inline_keyboard: bool = Field(...)
    keyboard: bool = Field(...)
    lang_id: int = Field(...)


class CoordinatesObject(BaseModel):
    latitude: float = Field(...)
    longitude: float = Field(...)


class GeoObject(BaseModel):
    type: str = Field(...)
    coordinates: CoordinatesObject = Field(...)


class MessageObject(BaseModel):
    attachments: List[dict] = Field(...)
    conversation_message_id: int = Field(...)
    date: int = Field(...)
    from_id: str = Field(...)
    peer_id: str = Field(...)
    random_id: int = Field(...)
    fwd_messages: List[dict] = Field(...)
    ref: Optional[str] = Field(None)
    id: int = Field(...)
    out: int = Field(...)
    important: bool = Field(...)
    is_hidden: bool = Field(...)
    text: str = Field(...)
    payload: Optional[str] = Field(None)
    geo: Optional[GeoObject] = Field(None)


class EventObject(BaseModel):
    client_info: ClientInfo = Field(...)
    message: MessageObject = Field(...)


class IncomingEvent(BaseModel):
    type: str = Field(...)
    group_id: int = Field(...)
    object: Optional[EventObject] = Field(None)
