from typing import Optional

from app.bot import vk_dispatcher
from app.bot.messages.vkontakte import (
    get_start_message,
    get_default_message,
    get_back_to_main_menu_message,
)
from app.cache import update_vk_cache_state
from app.db import get_db
from app.db.users import Users
from app.helpers.vkontakte import send_message, command, button_code
from app.schemas.vkontakte.incoming import IncomingEvent


@vk_dispatcher.register_handler(
    func=lambda event: command(event.object.message.payload) == "start"
)
async def vk_start_handler(event: IncomingEvent, state_data: Optional[dict] = None):
    """
    Хэндлер начала диалога (нажатие на кнопку "Начать")
    """

    db = await get_db()
    await Users.get_or_create_user(
        db,
        user_id=str(event.object.message.from_id),
        platform="tg",
    )
    state_data["state"] = None
    msg = await get_start_message(user_id=int(event.object.message.from_id))
    await send_message(msg)


@vk_dispatcher.register_handler(
    func=lambda event: button_code(event.object.message.payload) == "to_main_menu"
)
async def vk_back_to_main_menu_handler(event: IncomingEvent, state_data: dict):
    """
    Хэндлер для возврата в главное меню. Переводит в state = None
    """
    state_data["state"] = None
    await update_vk_cache_state(event.object.message.from_id, state_data)

    msg = await get_back_to_main_menu_message(user_id=int(event.object.message.from_id))
    await send_message(msg)


@vk_dispatcher.default_handler()
async def vk_default_handler(event: IncomingEvent, state_data: Optional[dict] = None):
    """
    Дефолтный хэндлер, в него проваливаются все события если не найден иной хэндлер
    """
    msg = await get_default_message(user_id=int(event.object.message.from_id))
    state_data["state"] = None
    await update_vk_cache_state(event.object.message.from_id, state_data)
    await send_message(msg)
