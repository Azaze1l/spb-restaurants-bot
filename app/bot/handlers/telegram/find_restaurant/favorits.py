from app.bot import tg_dispatcher
from app.bot.handlers.telegram.find_restaurant.services import show_5_of_restaurants
from app.bot.messages.telegram import (
    get_choose_type_of_food_message,
)

from app.cache import update_tg_cache_state
from app.db import get_db
from app.db.restaurants import Restaurants
from app.helpers.telegram import send_message
from app.schemas.telegram.incoming import Update
from app.config import settings
from app.schemas.telegram.outgoing import Message


@tg_dispatcher.register_handler(
    message_func=lambda: ("show_favorite_restaurants_button", "✨ Избранное"),
    state_data_func=lambda state_data: state_data["state"] == "find_restaurant",
)
async def tg_find_restaurant_handler(update: Update, state_data: dict):
    state_data["state"] = "find_restaurant|find_by_category|favorites"

    db = await get_db()
    favorites = await Restaurants.get_user_favorites_restaurants(
        db, str(update.message.from_.id)
    )
    if favorites:
        await show_5_of_restaurants(favorites, 0, update.message.from_.id)
    else:
        await send_message(
            Message(
                chat_id=update.message.from_.id,
                text="Похоже вы еще не добавили ничего в избранное........... я хочу спать",
            )
        )
        return

    await update_tg_cache_state(update.message.from_.id, state_data)
