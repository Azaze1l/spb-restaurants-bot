import logging

from app.bot import tg_dispatcher
from app.bot.messages.telegram import get_find_restaurant_message

from app.cache import update_tg_cache_state
from app.helpers.telegram import send_message
from app.schemas.telegram.incoming import Update
from app.config import settings

logger = logging.getLogger("events")


@tg_dispatcher.register_handler(
    message_func=lambda: ("find_restaurant_button", "🔎 Где ресторан"),
    state_data_func=lambda state_data: state_data["state"] is None,
)
async def tg_find_restaurant_handler(update: Update, state_data: dict):
    """
    Хэндлер начала сценария поиска ресторана. Переводит в state = find_restaurant
    """
    state_data["state"] = "find_restaurant"

    msg = await get_find_restaurant_message(chat_id=update.message.from_.id)
    await send_message(msg)
    await update_tg_cache_state(update.message.from_.id, state_data)
