from app.bot import vk_dispatcher
from app.bot.handlers.vkontakte.find_restaurant.services import show_5_of_restaurants
from app.bot.messages.vkontakte import (
    get_request_location_message,
    get_waiting_for_location_keyboard,
    get_find_restaurant_by_location_message,
    get_find_restaurant_message,
)
from app.cache import update_vk_cache_state
from app.db import get_db
from app.db.districts import CityDistricts
from app.db.restaurants import Restaurants
from app.helpers.vkontakte import command, send_message, button_code
from app.schemas.vkontakte.incoming import IncomingEvent
from app.schemas.vkontakte.outgoing import Message


@vk_dispatcher.register_handler(
    func=lambda event: button_code(event.object.message.payload) == "by_location",
    state_data_func=lambda state_data: state_data["state"] == "find_restaurant",
)
async def vk_find_restaurant_by_location_handler(
    event: IncomingEvent, state_data: dict
):
    state_data["state"] = "find_restaurant|waiting_for_location"
    msg = await get_request_location_message(int(event.object.message.from_id))
    msg.keyboard = await get_waiting_for_location_keyboard()
    await update_vk_cache_state(event.object.message.from_id, state_data)
    await send_message(msg)


@vk_dispatcher.register_handler(
    func=lambda event: button_code(event.object.message.payload) == "location",
    state_data_func=lambda state_data: state_data["state"]
    in ["find_restaurant|waiting_for_location"],
)
async def vk_restaurant_location_handler(event: IncomingEvent, state_data: dict):
    longitude = event.object.message.geo.coordinates.longitude
    latitude = event.object.message.geo.coordinates.latitude

    state_data["lat"] = latitude
    state_data["lon"] = longitude
    state_data["state"] = "find_restaurant|by_location"
    msg = await get_find_restaurant_by_location_message(
        int(event.object.message.from_id)
    )

    await update_vk_cache_state(event.object.message.from_id, state_data)
    await send_message(msg)


@vk_dispatcher.register_handler(
    func=lambda event: button_code(event.object.message.payload) == "by_nearest",
    state_data_func=lambda state_data: state_data["state"]
    == "find_restaurant|by_location",
)
async def vk_find_nearest_restaurants_handler(event: IncomingEvent, state_data: dict):
    state_data["state"] = "find_restaurant|by_location|nearest"
    db = await get_db()
    lat = state_data["lat"]
    lon = state_data["lon"]
    restaurants = await Restaurants.get_nearest_restaurants(db, lon, lat)
    last_elem_index = await show_5_of_restaurants(
        restaurants,
        0,
        user_id=int(event.object.message.from_id),
    )
    state_data["last_restaurant_index"] = last_elem_index
    state_data["count_of_restaurants"] = len(restaurants)
    await update_vk_cache_state(event.object.message.from_id, state_data)


@vk_dispatcher.register_handler(
    func=lambda event: button_code(event.object.message.payload) == "by_district",
    state_data_func=lambda state_data: state_data["state"]
    == "find_restaurant|by_location",
)
async def vk_find_restaurants_in_current_district_handler(
    event: IncomingEvent, state_data: dict
):
    state_data["state"] = "find_restaurant|by_location|district"
    db = await get_db()
    lat = state_data["lat"]
    lon = state_data["lon"]
    districts = await CityDistricts.get_district_by_current_coords(db, lon, lat)
    if not districts:
        msg = Message(
            user_id=int(event.object.message.from_id),
            message="К сожалению наш бот работает только в пределах Спб :(",
        )
        await send_message(msg)
    district_name = districts[0]["name"]
    restaurants = await Restaurants.get_restaurants_by_district_name(db, district_name)
    if not restaurants:
        msg = Message(
            user_id=int(event.object.message.from_id),
            message="Кажется в вашем районе еще не обнаружили крутых ресторанов :(",
        )
        await send_message(msg)
    last_elem_index = await show_5_of_restaurants(
        restaurants,
        0,
        user_id=event.object.message.from_id,
    )
    state_data["last_restaurant_index"] = last_elem_index
    state_data["count_of_restaurants"] = len(restaurants)
    state_data["district_name"] = district_name
    await update_vk_cache_state(event.object.message.from_id, state_data)


@vk_dispatcher.register_handler(
    state_data_func=lambda state_data: state_data["state"]
    in [
        "find_restaurant|waiting_for_location",
        "find_restaurant|by_location",
        "find_restaurant|by_location|district",
        "find_restaurant|by_location|nearest",
    ],
    func=lambda event: button_code(event.object.message.payload) == "back",
)
async def vk_back_to_prev_step_of_finding_restaurant_handler(
    event: IncomingEvent, state_data: dict
):
    """
    Хэндлер возврата назад в поиске ресторана
    """
    if state_data["state"] == "find_restaurant|waiting_for_location":
        state_data["state"] = "find_restaurant"
        msg = await get_find_restaurant_message(
            user_id=int(event.object.message.from_id)
        )
        await send_message(msg)
        await update_vk_cache_state(event.object.message.from_id, state_data)
    elif state_data["state"] == "find_restaurant|by_location":
        state_data["state"] = "find_restaurant|waiting_for_location"
        msg = await get_request_location_message(int(event.object.message.from_id))
        msg.reply_markup = await get_waiting_for_location_keyboard()
        await send_message(msg)
        await update_vk_cache_state(event.object.message.from_id, state_data)
    elif state_data["state"] in [
        "find_restaurant|by_location|district",
        "find_restaurant|by_location|nearest",
    ]:
        state_data["state"] = "find_restaurant|by_location"
        msg = await get_find_restaurant_by_location_message(
            int(event.object.message.from_id)
        )
        await send_message(msg)
        await update_vk_cache_state(event.object.message.from_id, state_data)
