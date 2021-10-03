from typing import Optional, List, Union

from pydantic import Field
from pydantic.main import BaseModel


class SetWebhookParams(BaseModel):
    url: str = Field(...)
    ip_address: Optional[str] = Field(None)
    max_connections: Optional[int] = Field(None)
    allowed_updates: Optional[List[str]] = Field(None)


class WebhookInfo(BaseModel):
    url: str = Field(...)
    has_custom_certificate: Optional[bool] = Field(None)
    pending_update_count: Optional[int] = Field(None)
    ip_address: Optional[str] = Field(None)
    last_error_date: Optional[int] = Field(None)
    last_error_message: Optional[str] = Field(None)
    max_connections: Optional[int] = Field(None)
    allowed_updates: Optional[List[str]] = Field(None)


class InlineKeyboardButton(BaseModel):
    text: str = Field(...)
    url: Optional[str] = Field(None)
    callback_data: Optional[str] = Field(None)


class InlineKeyboardMarkup(BaseModel):
    inline_keyboard: List[List[InlineKeyboardButton]] = Field(...)


class KeyboardButton(BaseModel):
    text: str = Field(...)
    request_contact: Optional[bool] = Field(None)
    request_location: Optional[bool] = Field(None)


class ReplyKeyboardMarkup(BaseModel):
    keyboard: List[List[KeyboardButton]] = Field(...)
    resize_keyboard: Optional[bool] = Field(None)
    one_time_keyboard: Optional[bool] = Field(None)


class Message(BaseModel):
    chat_id: int = Field(...)
    text: str = Field(...)
    reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = Field(
        None
    )
