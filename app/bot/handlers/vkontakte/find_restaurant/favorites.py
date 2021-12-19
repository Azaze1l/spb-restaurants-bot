from app.bot import vk_dispatcher
from app.bot.handlers.vkontakte.find_restaurant.services import show_5_of_restaurants
from app.cache import update_vk_cache_state
from app.db import get_db
from app.db.restaurants import Restaurants
from app.helpers.vkontakte import send_message, command, button_code
from app.schemas.vkontakte.incoming import IncomingEvent
from app.schemas.vkontakte.outgoing import Message


@vk_dispatcher.register_handler(
    func=lambda event: button_code(event.object.message.payload) == "favorites",
    state_data_func=lambda state_data: state_data["state"] == "find_restaurant",
)
async def vk_find_restaurant_handler(event: IncomingEvent, state_data: dict):
    state_data["state"] = "find_restaurant|find_by_category|favorites"

    db = await get_db()
    favorites = await Restaurants.get_user_favorites_restaurants(
        db, str(event.object.message.from_id)
    )
    if favorites:
        await show_5_of_restaurants(favorites, 0, event.object.message.from_id)
    else:
        await send_message(
            Message(
                user_id=event.object.message.from_id,
                message="Похоже вы еще не добавили ничего в избранное........... я хочу спать",
            )
        )
        return

    await update_vk_cache_state(event.object.message.from_id, state_data)
