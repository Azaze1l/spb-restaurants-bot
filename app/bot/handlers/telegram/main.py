from app.bot import tg_dispatcher
from app.bot.messages.telegram import (
    get_start_message,
    get_default_message,
    get_back_to_main_menu_message,
)
from app.cache import update_tg_cache_state
from app.helpers.telegram import send_message
from app.schemas.telegram.incoming import Update


@tg_dispatcher.register_handler(
    message_func=lambda update: update.message.text.startswith("/start")
)
async def tg_start_handler(update: Update, state_data: dict):
    """
    Хэндлер начала диалога (нажатие на кнопку "Start")
    """
    state_data["state"] = None
    await update_tg_cache_state(update.message.from_.id, state_data)

    msg = await get_start_message(chat_id=update.message.from_.id)
    await send_message(msg)


@tg_dispatcher.register_handler(
    message_func=lambda: ("to_main_menu_button", "↩️ В главное меню")
)
async def tg_back_to_main_menu_handler(update: Update, state_data: dict):
    """
    Хэндлер для возврата в главное меню. Переводит в state = None
    """
    state_data["state"] = None
    await update_tg_cache_state(update.message.from_.id, state_data)

    msg = await get_back_to_main_menu_message(chat_id=update.message.from_.id)
    await send_message(msg)


@tg_dispatcher.default_handler()
async def tg_default_handler(update: Update, state_data: dict):
    """
    Дефолтный хэндлер, в него проваливаются все события если не найден иной хэндлер
    """
    state_data["state"] = None
    if update.message is not None:
        chat_id = update.message.from_.id
        await update_tg_cache_state(chat_id, state_data)
    else:
        chat_id = update.callback_query.from_.id
        await update_tg_cache_state(chat_id, state_data)
    msg = await get_default_message(chat_id=chat_id)

    await send_message(msg)
