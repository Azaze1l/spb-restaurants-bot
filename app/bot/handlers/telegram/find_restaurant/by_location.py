from app.bot import tg_dispatcher
from app.bot.handlers.telegram.find_restaurant.services import (
    show_5_of_restaurants,
)
from app.bot.messages.telegram import (
    get_find_restaurant_by_location_message,
    get_request_location_message,
    get_waiting_for_location_keyboard,
)
from app.cache import update_tg_cache_state
from app.db import get_db
from app.db.districts import CityDistricts
from app.db.restaurants import Restaurants
from app.helpers.telegram import send_message
from app.schemas.telegram.incoming import Update
from app.schemas.telegram.outgoing import Message


@tg_dispatcher.register_handler(
    message_func=lambda: ("find_by_location_button", "📍Найти по местоположению"),
    state_data_func=lambda state_data: state_data["state"] == "find_restaurant",
)
async def tg_find_restaurant_by_location_handler(update: Update, state_data: dict):
    state_data["state"] = "find_restaurant|by_location"
    msg = await get_request_location_message(update.message.chat.id)
    msg.reply_markup = await get_waiting_for_location_keyboard()
    await update_tg_cache_state(update.message.chat.id, state_data)
    await send_message(msg)


@tg_dispatcher.register_handler(
    message_func=lambda update: update.message.location is not None,
    state_data_func=lambda state_data: state_data["state"]
    in ["find_restaurant|by_location"],
)
async def tg_restaurant_location_handler(update: Update, state_data: dict):
    longitude = update.message.location.longitude
    latitude = update.message.location.latitude

    state_data["lat"] = latitude
    state_data["lon"] = longitude
    state_data["state"] = "find_restaurant|by_location"
    msg = await get_find_restaurant_by_location_message(update.message.from_.id)

    await update_tg_cache_state(update.message.from_.id, state_data)
    await send_message(msg)


@tg_dispatcher.register_handler(
    message_func=lambda: ("find_by_location_button", "📍 Найти ближайшие рестораны"),
    state_data_func=lambda state_data: state_data["state"]
    == "find_restaurant|by_location",
)
async def tg_find_nearest_restaurants_handler(update: Update, state_data: dict):
    state_data["state"] = "find_restaurant|by_location|nearest"
    db = await get_db()
    lat = state_data["lat"]
    lon = state_data["lon"]
    restaurants = await Restaurants.get_nearest_restaurants(db, lon, lat)
    last_elem_index = await show_5_of_restaurants(
        restaurants,
        0,
        chat_id=update.message.from_.id,
    )
    state_data["last_restaurant_index"] = last_elem_index
    state_data["count_of_restaurants"] = len(restaurants)
    await update_tg_cache_state(update.message.from_.id, state_data)


@tg_dispatcher.register_handler(
    message_func=lambda: ("find_by_location_button", "🪧 Найти в текущем районе"),
    state_data_func=lambda state_data: state_data["state"]
    == "find_restaurant|by_location",
)
async def tg_find_restaurants_in_current_district_handler(
    update: Update, state_data: dict
):
    state_data["state"] = "find_restaurant|by_location|district"
    db = await get_db()
    lat = state_data["lat"]
    lon = state_data["lon"]
    districts = await CityDistricts.get_district_by_current_coords(db, lon, lat)
    if not districts:
        msg = Message(
            chat_id=update.message.from_.id,
            text="К сожалению наш бот работает только в пределах Спб :(",
        )
        await send_message(msg)
    district_name = districts[0]["name"]
    restaurants = await Restaurants.get_restaurants_by_district_name(db, district_name)
    if not restaurants:
        msg = Message(
            chat_id=update.message.from_.id,
            text="Кажется в вашем районе еще не обнаружили крутых ресторанов :(",
        )
        await send_message(msg)
    last_elem_index = await show_5_of_restaurants(
        restaurants,
        0,
        chat_id=update.message.from_.id,
    )
    state_data["last_restaurant_index"] = last_elem_index
    state_data["count_of_restaurants"] = len(restaurants)
    await update_tg_cache_state(update.message.from_.id, state_data)
