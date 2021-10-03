import logging
from typing import Optional

import httpx

from app.config import settings
from app.schemas.telegram.outgoing import (
    WebhookInfo,
    SetWebhookParams,
    Message,
    InlineKeyboardMarkup,
)

logger = logging.getLogger("events")

TG_BASE_URL = f"https://api.telegram.org/bot{settings.TG_TOKEN}/"


async def getWebhookInfo() -> Optional[WebhookInfo]:
    url = TG_BASE_URL + "getWebhookInfo"
    async with httpx.AsyncClient() as client:
        r = await client.post(url)
    data = r.json()
    if data["ok"] is True:
        return WebhookInfo(**data["result"])
    return None


async def setWebhook():
    url = TG_BASE_URL + "setWebhook"
    webhook_url = f"https://{settings.DOMAIN}/api/bot/telegram"
    params = SetWebhookParams(url=webhook_url)
    data = params.dict(exclude_none=True)
    async with httpx.AsyncClient() as client:
        r = await client.post(url, data=data)


async def set_webhook_on_startup():
    logger.info("Checking current Webhook configuration")
    wb_info = await getWebhookInfo()
    if wb_info is None or wb_info.url != f"https://{settings.DOMAIN}/api/bot/telegram":
        logger.info("Webhook configuration mismatch. Updating configuration.")
        await setWebhook()


async def send_message(message: Message):
    url = TG_BASE_URL + "sendMessage"
    data = message.dict(exclude_none=True)
    data.update({"parse_mode": "Markdown"})
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=data)


async def edit_message_text(chat_id, message_id, text):
    url = TG_BASE_URL + "editMessageText"
    data = {"chat_id": chat_id, "message_id": message_id, "text": text}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=data)


async def edit_message_caption(chat_id, message_id, caption):
    url = TG_BASE_URL + "editMessageCaption"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "caption": caption,
        "parse_mode": "Markdown",
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=data)


async def edit_message_reply_markup(
    chat_id, message_id, reply_markup: InlineKeyboardMarkup
):
    url = TG_BASE_URL + "editMessageReplyMarkup"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": reply_markup.dict(exclude_none=True),
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=data)


async def send_location(chat_id, latitude, longitude):
    url = TG_BASE_URL + "sendLocation"
    data = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=data)


async def send_photo(chat_id, photo, caption=None, reply_markup=None):
    url = TG_BASE_URL + "sendPhoto"
    data = {
        "chat_id": chat_id,
        "photo": photo,
        "caption": caption,
        "reply_markup": reply_markup,
        "parse_mode": "Markdown",
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=data)
