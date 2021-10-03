import logging
from pprint import pprint

from fastapi import APIRouter, Depends
from starlette.responses import Response

from app.bot import vk_dispatcher, tg_dispatcher
from app.bot.messages import get_modifiable_items
from app.cache import get_state_cache
from app.config import settings
from app.db import get_db
from app.helpers.vkontakte import send_message
from app.schemas.telegram.incoming import Update
from app.schemas.vkontakte.incoming import IncomingEvent
from app.schemas.vkontakte.outgoing import Message

bot_router = APIRouter()
logger = logging.getLogger("events")


@bot_router.post("/telegram")
async def process_telegram_events(
    update: Update, db=Depends(get_db), state_cache=Depends(get_state_cache)
):
    state_cache_service = get_state_cache()

    if settings.LOG_INCOMING_EVENTS:
        logger.info(f"Incoming Telegram event: {update.dict()}")

    if update.message is not None:
        user_id = update.message.from_.id
    elif update.callback_query is not None:
        user_id = update.callback_query.from_.id
    else:
        logger.warning(f"Unsupported Telegram event: {update.dict()}")
        return ""

    state_data_key = f"tg:{user_id}"
    state_data = await state_cache_service.get_cache(state_data_key)
    if state_data is None:
        state_data = {"state": None}
        await state_cache_service.set_cache(state_data_key, state_data)
    logger.info(f"State data before processing event: {state_data}")
    modifiable_items = await get_modifiable_items()
    await tg_dispatcher.process_event(
        event=update, state_data=state_data, modifiable_items=modifiable_items
    )

    return ""


@bot_router.post("/vkontakte")
async def process_vkontakte_events(
    event: IncomingEvent, db=Depends(get_db), state_cache=Depends(get_state_cache)
):
    state_cache_service = get_state_cache()

    if settings.LOG_INCOMING_EVENTS:
        logger.info(f"Incoming VKontakte event: {event.dict()}")

    if event.type == "confirmation":
        return Response(content=settings.VK_CONFIRMATION_TOKEN)
    else:
        state_data_key = f"vk:{event.object.message.from_id}"
        state_data = await state_cache_service.get_cache(state_data_key)
        if state_data is None:
            state_data = {"state": None}
            await state_cache_service.set_cache(state_data_key, state_data)
        logger.info(f"State data before processing event: {state_data}")
        await vk_dispatcher.process_event(event=event, state_data=state_data)

    return Response(content="ok")


from app.bot.handlers import *
