import json
import logging
from io import BytesIO
from typing import Optional, List
import PIL
from PIL import Image
import httpx
from urllib.request import urlopen

from app.cache import logger
from app.config import settings
from app.schemas.vkontakte.outgoing import Message

MESSAGES_URL = f"https://api.vk.com/method/messages.send"
EDIT_MESSAGE_URL = f"https://api.vk.com/method/messages.edit"
DELETE_MESSAGE_URL = f"https://api.vk.com/method/messages.delete"
GET_MESSAGES_UPLOAD_SERVER_URL = (
    f"https://api.vk.com/method/photos.getMessagesUploadServer"
)
SAVE_MESSAGES_PHOTO_URL = f"https://api.vk.com/method/photos.saveMessagesPhoto"
UPLOAD_PHOTO_URL = f"https://api.vk.com/method/photos.getMessagesUploadServer"


def command(json_payload: Optional[str] = None):
    if json_payload is None:
        return ""
    return json.loads(json_payload).get("command")


def button_code(json_payload: str):
    if json_payload is None:
        return ""
    return json.loads(json_payload).get("button")


async def send_message(message: Message):
    async with httpx.AsyncClient() as client:
        data = message.dict(exclude_none=True)
        if data.get("keyboard"):
            data["keyboard"] = json.dumps(data["keyboard"], ensure_ascii=False).encode(
                "utf-8"
            )
        if data.get("template"):
            data["template"] = json.dumps(data["template"], ensure_ascii=False).encode(
                "utf-8"
            )
        data["access_token"] = settings.VK_TOKEN
        data["v"] = settings.VK_API_VERSION
        r = await client.post(MESSAGES_URL, data=data)
        logger.info(r.json())


async def uploadPhoto(s3_photo_url: str, server_url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(s3_photo_url)
    img_data = BytesIO(r.content)
    img_data.seek(0)
    ext = s3_photo_url.split(".")[-1]
    files = {"photo": (f"photo.{ext}", img_data)}
    async with httpx.AsyncClient() as client:
        r = await client.post(server_url, files=files)
        logger.info(r.json())
    return r.json()


async def savePhoto(uploaded_photo: dict):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            SAVE_MESSAGES_PHOTO_URL,
            data={
                **uploaded_photo,
                "access_token": settings.VK_TOKEN,
                "v": settings.VK_API_VERSION,
            },
        )
        logger.info(r.json())
    return r.json()["response"][0]


async def edit_message_keyboard(user_id, message_id, keyboard):
    async with httpx.AsyncClient() as client:
        data = dict(user_id=user_id, message_id=message_id, keyboard=keyboard)
        data["access_token"] = settings.VK_TOKEN
        data["v"] = settings.VK_API_VERSION
        r = await client.post(EDIT_MESSAGE_URL, data=data)
        logger.info(r.json())


async def delete_message(message_ids: List):
    async with httpx.AsyncClient() as client:
        data = dict(message_ids=message_ids)
        data["access_token"] = settings.VK_TOKEN
        data["v"] = settings.VK_API_VERSION
        r = await client.post(DELETE_MESSAGE_URL, data=data)
        logger.info(r.json())


async def get_photo_attachment(photo):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            UPLOAD_PHOTO_URL,
            data={"access_token": settings.VK_TOKEN, "v": settings.VK_API_VERSION},
        )
        print(r.json())
        url = r.json()["response"]["upload_url"]

    uploaded_photo = await uploadPhoto(photo, url)
    saved_photo = await savePhoto(uploaded_photo)
    attachment = f"photo{saved_photo['owner_id']}_{saved_photo['id']}_{saved_photo['access_key']}"
    return attachment
