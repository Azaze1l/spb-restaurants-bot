from typing import Optional, List

from pydantic import Field
from pydantic.main import BaseModel


class FileBasedObject(BaseModel):
    file_id: str = Field(...)
    file_unique_id: str = Field(...)
    file_size: Optional[int] = Field(None)


class Location(BaseModel):
    longitude: float = Field(...)
    latitude: float = Field(...)
    horizontal_accuracy: Optional[float] = Field(None)
    live_period: Optional[int] = Field(None)
    heading: Optional[int] = Field(None)
    proximity_alert_radius: Optional[int] = Field(None)


class Contact(BaseModel):
    phone_number: str = Field(...)
    first_name: str = Field(...)
    last_name: Optional[str] = Field(None)
    user_id: Optional[int] = Field(None)
    vcard: Optional[str] = Field(None)


class Voice(FileBasedObject):
    duration: int = Field(...)
    mime_type: Optional[str] = Field(None)


class Photo(FileBasedObject):
    width: int = Field(...)
    height: int = Field(...)


class MaskPosition(BaseModel):
    point: str = Field(...)
    x_shift: float = Field(...)
    y_shift: float = Field(...)
    scale: float = Field(...)


class Sticker(FileBasedObject):
    width: int = Field(...)
    height: int = Field(...)
    is_animated: bool = Field(...)
    thumb: Optional[Photo] = Field(None)
    emoji: Optional[str] = Field(None)
    set_name: Optional[str] = Field(None)
    mask_position: Optional[MaskPosition] = Field(None)


class VideoNote(FileBasedObject):
    length: int = Field(...)
    duration: int = Field(...)
    thumb: Optional[Photo] = Field(None)


class Video(FileBasedObject):
    width: int = Field(...)
    height: int = Field(...)
    duration: int = Field(...)
    thumb: Optional[Photo] = Field(None)
    file_name: Optional[str] = Field(None)
    mime_type: Optional[str] = Field(None)


class Document(FileBasedObject):
    thumb: Optional[Photo] = Field(None)
    file_name: Optional[str] = Field(None)
    mime_type: Optional[str] = Field(None)


class Audio(FileBasedObject):
    duration: int = Field(...)
    performer: Optional[str] = Field(None)
    title: Optional[str] = Field(None)
    file_name: Optional[str] = Field(None)
    mime_type: Optional[str] = Field(None)
    thumb: Optional[Photo] = Field(None)


class Chat(BaseModel):
    id: int = Field(...)
    type: str = Field(...)
    title: Optional[str] = Field(None)
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    username: Optional[str] = Field(None)


class User(BaseModel):
    id: int = Field(...)
    is_bot: bool = Field(...)
    first_name: str = Field(...)
    last_name: Optional[str] = Field(None)
    username: Optional[str] = Field(None)
    language_code: Optional[str] = Field(None)
    can_join_groups: Optional[bool] = Field(None)
    can_read_all_group_messages: Optional[bool] = Field(None)
    supports_inline_queries: Optional[bool] = Field(None)


class Message(BaseModel):
    message_id: int = Field(...)
    date: int = Field(...)
    from_: Optional[User] = Field(None)
    chat: Optional[Chat] = Field(None)
    text: Optional[str] = Field(None)
    caption: Optional[str] = Field(None)
    audio: Optional[Audio] = Field(None)
    document: Optional[Document] = Field(None)
    photo: Optional[List[Photo]] = Field(None)
    sticker: Optional[Sticker] = Field(None)
    video: Optional[Video] = Field(None)
    video_note: Optional[VideoNote] = Field(None)
    voice: Optional[Voice] = Field(None)
    contact: Optional[Contact] = Field(None)
    location: Optional[Location] = Field(None)

    class Config:
        fields = {"from_": "from"}


class CallbackQuery(BaseModel):
    id: int = Field(...)
    from_: Optional[User] = Field(None)
    message: Optional[Message] = Field(None)
    inline_message_id: Optional[int] = Field(None)
    chat_instance: Optional[str] = Field(None)
    data: Optional[str] = Field(None)
    game_short_name: Optional[str] = Field(None)

    class Config:
        fields = {"from_": "from"}


class Update(BaseModel):
    update_id: int = Field(...)
    message: Optional[Message] = Field(None)
    edited_message: Optional[Message] = Field(None)
    callback_query: Optional[CallbackQuery] = Field(None)
