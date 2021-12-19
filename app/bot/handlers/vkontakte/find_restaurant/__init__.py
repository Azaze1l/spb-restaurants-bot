from app.bot import vk_dispatcher
from app.bot.messages.vkontakte import get_find_restaurant_message
from app.cache import update_vk_cache_state
from app.helpers.vkontakte import send_message, button_code
from app.schemas.vkontakte.incoming import IncomingEvent


@vk_dispatcher.register_handler(
    func=lambda event: button_code(event.object.message.payload) == "find_restaurant",
    state_data_func=lambda state_data: state_data["state"] is None,
)
async def tg_find_restaurant_handler(event: IncomingEvent, state_data: dict):
    """
    Хэндлер начала сценария поиска ресторана. Переводит в state = find_restaurant
    """
    state_data["state"] = "find_restaurant"

    msg = await get_find_restaurant_message(user_id=int(event.object.message.from_id))
    await send_message(msg)
    await update_vk_cache_state(event.object.message.from_id, state_data)
