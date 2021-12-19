from app.bot import vk_dispatcher
from app.bot.handlers.vkontakte.find_restaurant.services import process_filters_state
from app.bot.handlers.vkontakte.find_restaurant.services import show_5_of_restaurants
from app.bot.messages.vkontakte import (
    get_choose_type_of_food_message,
    get_choose_type_of_restaurant_message,
    get_choose_type_of_meal_message,
    get_step_back_keyboard,
    get_find_restaurant_message,
    get_in_favorite_inline_keyboard,
)
from app.cache import update_vk_cache_state
from app.config import settings
from app.db import get_db
from app.db.restaurants import Restaurants
from app.helpers.vkontakte import (
    send_message,
    edit_message_keyboard,
    delete_message,
    button_code,
)
from app.schemas.vkontakte.incoming import IncomingEvent
from app.schemas.vkontakte.outgoing import Message


@vk_dispatcher.register_handler(
    func=lambda event: button_code(event.object.message.payload)
    == "by_list_of_proposed",
    state_data_func=lambda state_data: state_data["state"] == "find_restaurant",
)
async def vk_find_restaurant_handler(event: IncomingEvent, state_data: dict):
    state_data["state"] = "find_restaurant|find_by_category|food_type"
    state_data["food_filters_state"] = settings.TYPE_OF_FOOD_FILTERS
    state_data["restaurant_filters_state"] = settings.TYPE_OF_RESTAURANT_FILTERS
    state_data["meal_filters_state"] = settings.TYPE_OF_MEAL_FILTERS

    msg = await get_choose_type_of_food_message(
        user_id=int(event.object.message.from_id),
        food_filters_state=state_data["food_filters_state"],
    )

    await update_vk_cache_state(event.object.message.from_id, state_data)
    await send_message(msg)


@vk_dispatcher.register_handler(
    func=lambda event: button_code(event.object.message.payload) == "next",
    state_data_func=lambda state_data: state_data["state"]
    in [
        "find_restaurant|find_by_category|food_type",
        "find_restaurant|find_by_category|restaurant_type",
        "find_restaurant|find_by_category|meal_type",
    ],
)
async def vk_steps_to_show_restaurants_handler(event: IncomingEvent, state_data: dict):
    if state_data["state"] == "find_restaurant|find_by_category|food_type":
        state_data["state"] = "find_restaurant|find_by_category|restaurant_type"

        msg = await get_choose_type_of_restaurant_message(
            user_id=int(event.object.message.from_id),
            restaurant_filters_state=state_data["restaurant_filters_state"],
        )
        await update_vk_cache_state(event.object.message.from_id, state_data)
        await send_message(msg)
    elif state_data["state"] == "find_restaurant|find_by_category|restaurant_type":
        state_data["state"] = "find_restaurant|find_by_category|meal_type"

        msg = await get_choose_type_of_meal_message(
            user_id=int(event.object.message.from_id),
            meal_filters_state=state_data["meal_filters_state"],
        )
        await update_vk_cache_state(event.object.message.from_id, state_data)
        await send_message(msg)
    elif state_data["state"] == "find_restaurant|find_by_category|meal_type":
        state_data["state"] = "find_restaurant|find_by_category|showing_restaurants"
        db = await get_db()
        restaurants = await Restaurants.get_restaurants_using_searching_filters(
            db,
            filters=state_data["restaurant_filters_state"]
            + state_data["food_filters_state"]
            + state_data["meal_filters_state"],
        )
        keyboard = await get_step_back_keyboard()
        await send_message(
            Message(
                user_id=event.object.message.from_id,
                message="Приятного отдыха!!",
                keyboard=keyboard,
            )
        )

        last_elem_index = await show_5_of_restaurants(
            restaurants,
            0,
            user_id=event.object.message.from_id,
        )
        state_data["last_restaurant_index"] = last_elem_index
        state_data["count_of_restaurants"] = len(restaurants)
        await update_vk_cache_state(event.object.message.from_id, state_data)


@vk_dispatcher.register_handler(
    state_data_func=lambda state_data: state_data["state"]
    in [
        "find_restaurant|find_by_category|food_type",
        "find_restaurant|find_by_category|restaurant_type",
        "find_restaurant|find_by_category|meal_type",
        "find_restaurant|find_by_category|showing_restaurants",
    ],
    func=lambda event: button_code(event.object.message.payload) == "back",
)
async def vk_back_to_prev_step_of_finding_restaurant_handler(
    event: IncomingEvent, state_data: dict
):
    """
    Хэндлер возврата назад в поиске ресторана
    """
    if state_data["state"] == "find_restaurant|find_by_category|food_type":
        state_data["state"] = "find_restaurant"
        msg = await get_find_restaurant_message(
            user_id=int(event.object.message.from_id)
        )
        await send_message(msg)
        await update_vk_cache_state(event.object.message.from_id, state_data)
    elif state_data["state"] == "find_restaurant|find_by_category|restaurant_type":
        state_data["state"] = "find_restaurant|find_by_category|food_type"
        msg = await get_choose_type_of_food_message(
            user_id=int(event.object.message.from_id),
            food_filters_state=state_data["food_filters_state"],
        )
        await send_message(msg)
        await update_vk_cache_state(event.object.message.from_id, state_data)
    elif state_data["state"] == "find_restaurant|find_by_category|meal_type":
        state_data["state"] = "find_restaurant|find_by_category|restaurant_type"
        msg = await get_choose_type_of_restaurant_message(
            user_id=int(event.object.message.from_id),
            restaurant_filters_state=state_data["restaurant_filters_state"],
        )
        await send_message(msg)
        await update_vk_cache_state(event.object.message.from_id, state_data)
    elif state_data["state"] == "find_restaurant|find_by_category|showing_restaurants":
        state_data["state"] = "find_restaurant|find_by_category|meal_type"
        msg = await get_choose_type_of_meal_message(
            user_id=int(event.object.message.from_id),
            meal_filters_state=state_data["meal_filters_state"],
        )
        await send_message(msg)
        await update_vk_cache_state(event.object.message.from_id, state_data)


@vk_dispatcher.register_handler(
    func=lambda event: button_code(event.object.message.payload) == "change_filters",
    state_data_func=lambda state_data: state_data["state"]
    in [
        "find_restaurant|find_by_category|food_type",
        "find_restaurant|find_by_category|restaurant_type",
        "find_restaurant|find_by_category|meal_type",
    ],
)
async def vk_process_restaurant_filters_states_handler(
    event: IncomingEvent, state_data: dict
):
    filter_name = event.object.message.text[2::]

    if state_data["state"] == "find_restaurant|find_by_category|food_type":
        filters_state = state_data["food_filters_state"]
        state_data["filter_state"] = await process_filters_state(
            filters_state, filter_name, event
        )
        await update_vk_cache_state(event.object.message.from_id, state_data)
    elif state_data["state"] == "find_restaurant|find_by_category|restaurant_type":
        filters_state = state_data["restaurant_filters_state"]
        state_data["filter_state"] = await process_filters_state(
            filters_state, filter_name, event
        )
        await update_vk_cache_state(event.object.message.from_id, state_data)
    elif state_data["state"] == "find_restaurant|find_by_category|meal_type":
        filters_state = state_data["meal_filters_state"]
        state_data["filter_state"] = await process_filters_state(
            filters_state, filter_name, event
        )
        await update_vk_cache_state(event.object.message.from_id, state_data)


@vk_dispatcher.register_handler(
    func=lambda event: button_code(event.object.message.payload) == "show_more",
    state_data_func=lambda state_data: state_data["state"]
    in [
        "find_restaurant|find_by_category|showing_restaurants",
        "find_restaurant|find_by_category|favorites",
        "find_restaurant|by_location|district",
        "find_restaurant|by_location|nearest",
    ],
)
async def vk_show_more_restaurants_handler(event: IncomingEvent, state_data: dict):
    db = await get_db()
    user_favorites_restaurants = await Restaurants.get_user_favorites_restaurants(
        db, str(event.object.message.from_id)
    )
    await edit_message_keyboard(
        user_id=int(event.object.message.from_id),
        message_id=event.object.message.id,
        keyboard=get_in_favorite_inline_keyboard(
            event.object.message.text.split()[2], user_favorites_restaurants
        ),
    )
    if state_data["state"] == "find_restaurant|find_by_category|showing_restaurants":
        restaurants = await Restaurants.get_restaurants_using_searching_filters(
            db,
            filters=state_data["restaurant_filters_state"]
            + state_data["food_filters_state"]
            + state_data["meal_filters_state"],
        )
    elif state_data["state"] == "find_restaurant|find_by_category|favorites":
        restaurants = await Restaurants.get_user_favorites_restaurants(
            db, str(event.object.message.from_id)
        )
    elif state_data["state"] == "find_restaurant|by_location|district":
        district_name = state_data["district_name"]
        restaurants = await Restaurants.get_restaurants_by_district_name(
            db, district_name
        )
    else:
        lat = state_data["lat"]
        lon = state_data["lon"]
        restaurants = await Restaurants.get_nearest_restaurants(db, lon, lat)

    last_restaurant_index = int(event.object.message.payload.split()[1])
    last_elem_index = await show_5_of_restaurants(
        restaurants,
        last_restaurant_index,
        user_id=event.object.message.from_id,
    )
    state_data["last_restaurant_index"] = last_elem_index
    await update_vk_cache_state(event.object.message.from_id, state_data)


@vk_dispatcher.register_handler(
    func=lambda event: button_code(event.object.message.payload).startswith(
        "out_of_favorites"
    )
    or button_code(event.object.message.payload).startswith("in_favorites"),
    state_data_func=lambda state_data: state_data["state"]
    in [
        "find_restaurant|find_by_category|showing_restaurants",
        "find_restaurant|find_by_category|favorites",
    ],
)
async def vk_process_restaurant_favorite_state_handler(
    event: IncomingEvent, state_data: dict
):
    restaurant_id = event.object.message.payload.split()[1]
    has_show_more = event.object.message.payload.split()[2]

    if event.object.message.payload.startswith("in_favorites"):
        db = await get_db()
        favorites = await Restaurants.add_restaurant_to_favorites(
            db, restaurant_id, str(event.object.message.from_id)
        )

    else:
        db = await get_db()
        favorites = await Restaurants.remove_restaurant_from_favorites(
            db, restaurant_id, str(event.object.message.from_id)
        )
        if state_data["state"] == "find_restaurant|find_by_category|favorites":
            await delete_message(
                message_ids=[event.object.message.id],
            )
            return
    count_of_restaurants = state_data["count_of_restaurants"]
    last_elem_index = state_data["last_restaurant_index"]
    keyboard = get_in_favorite_inline_keyboard(
        restaurant_id,
        favorites,
        last_elem_index - 5 if last_elem_index is not None else None,
        count_of_restaurants,
        show_more=int(has_show_more),
    )
    await edit_message_keyboard(
        user_id=int(event.object.message.from_id),
        message_id=event.object.message.id,
        keyboard=keyboard,
    )
