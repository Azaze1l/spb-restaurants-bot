from app.bot import tg_dispatcher
from app.bot.handlers.telegram.find_restaurant.services import (
    process_filters_state,
    show_5_of_restaurants,
)
from app.bot.messages.telegram import (
    get_choose_type_of_food_message,
    get_choose_type_of_restaurant_message,
    get_choose_type_of_meal_message,
    get_find_restaurant_message,
    get_in_favorite_inline_keyboard,
    get_step_back_keyboard,
)

from app.cache import update_tg_cache_state
from app.db import get_db
from app.db.restaurants import Restaurants
from app.helpers.telegram import send_message, edit_message_reply_markup, delete_message
from app.schemas.telegram.incoming import Update
from app.config import settings
from app.schemas.telegram.outgoing import Message


@tg_dispatcher.register_handler(
    message_func=lambda: ("find_by_list_of_proposed_button", "📖 Найти по категориям"),
    state_data_func=lambda state_data: state_data["state"] == "find_restaurant",
)
async def tg_find_restaurant_handler(update: Update, state_data: dict):
    state_data["state"] = "find_restaurant|find_by_category|food_type"
    state_data["food_filters_state"] = settings.TYPE_OF_FOOD_FILTERS
    state_data["restaurant_filters_state"] = settings.TYPE_OF_RESTAURANT_FILTERS
    state_data["meal_filters_state"] = settings.TYPE_OF_MEAL_FILTERS

    msg = await get_choose_type_of_food_message(
        chat_id=update.message.from_.id,
        food_filters_state=state_data["food_filters_state"],
    )

    await update_tg_cache_state(update.message.from_.id, state_data)
    await send_message(msg)


@tg_dispatcher.register_handler(
    message_func=lambda update: update.message.text == "➡️Далее",
    state_data_func=lambda state_data: state_data["state"]
    in [
        "find_restaurant|find_by_category|food_type",
        "find_restaurant|find_by_category|restaurant_type",
        "find_restaurant|find_by_category|meal_type",
    ],
)
async def tg_steps_to_show_restaurants_handler(update: Update, state_data: dict):
    if state_data["state"] == "find_restaurant|find_by_category|food_type":
        state_data["state"] = "find_restaurant|find_by_category|restaurant_type"

        msg = await get_choose_type_of_restaurant_message(
            chat_id=update.message.from_.id,
            restaurant_filters_state=state_data["restaurant_filters_state"],
        )
        await update_tg_cache_state(update.message.from_.id, state_data)
        await send_message(msg)
    elif state_data["state"] == "find_restaurant|find_by_category|restaurant_type":
        state_data["state"] = "find_restaurant|find_by_category|meal_type"

        msg = await get_choose_type_of_meal_message(
            chat_id=update.message.from_.id,
            meal_filters_state=state_data["meal_filters_state"],
        )
        await update_tg_cache_state(update.message.from_.id, state_data)
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
                chat_id=update.message.from_.id,
                text="Приятного отдыха!!",
                reply_markup=keyboard,
            )
        )

        last_elem_index = await show_5_of_restaurants(
            restaurants,
            0,
            chat_id=update.message.from_.id,
        )
        state_data["last_restaurant_index"] = last_elem_index
        state_data["count_of_restaurants"] = len(restaurants)
        await update_tg_cache_state(update.message.from_.id, state_data)


@tg_dispatcher.register_handler(
    state_data_func=lambda state_data: state_data["state"]
    in [
        "find_restaurant|find_by_category|food_type",
        "find_restaurant|find_by_category|restaurant_type",
        "find_restaurant|find_by_category|meal_type",
        "find_restaurant|find_by_category|showing_restaurants",
    ],
    message_func=lambda: ("step_back_button", "⬅️ Назад"),
)
async def tg_back_to_prev_step_of_finding_restaurant_handler(
    update: Update, state_data: dict
):
    """
    Хэндлер возврата назад в поиске ресторана
    """
    if state_data["state"] == "find_restaurant|find_by_category|food_type":
        state_data["state"] = "find_restaurant"
        msg = await get_find_restaurant_message(chat_id=update.message.from_.id)
        await send_message(msg)
        await update_tg_cache_state(update.message.from_.id, state_data)
    elif state_data["state"] == "find_restaurant|find_by_category|restaurant_type":
        state_data["state"] = "find_restaurant|find_by_category|food_type"
        msg = await get_choose_type_of_food_message(
            chat_id=update.message.from_.id,
            food_filters_state=state_data["food_filters_state"],
        )
        await send_message(msg)
        await update_tg_cache_state(update.message.from_.id, state_data)
    elif state_data["state"] == "find_restaurant|find_by_category|meal_type":
        state_data["state"] = "find_restaurant|find_by_category|restaurant_type"
        msg = await get_choose_type_of_restaurant_message(
            chat_id=update.message.from_.id,
            restaurant_filters_state=state_data["restaurant_filters_state"],
        )
        await send_message(msg)
        await update_tg_cache_state(update.message.from_.id, state_data)
    elif state_data["state"] == "find_restaurant|find_by_category|showing_restaurants":
        state_data["state"] = "find_restaurant|find_by_category|meal_type"
        msg = await get_choose_type_of_meal_message(
            chat_id=update.message.from_.id,
            meal_filters_state=state_data["meal_filters_state"],
        )
        await send_message(msg)
        await update_tg_cache_state(update.message.from_.id, state_data)


@tg_dispatcher.register_handler(
    message_func=lambda update: update.message.text[2::]
    in [
        searching_filter.get("name")
        for searching_filter in settings.TYPE_OF_RESTAURANT_FILTERS
        + settings.TYPE_OF_MEAL_FILTERS
        + settings.TYPE_OF_FOOD_FILTERS
    ],
    state_data_func=lambda state_data: state_data["state"]
    in [
        "find_restaurant|find_by_category|food_type",
        "find_restaurant|find_by_category|restaurant_type",
        "find_restaurant|find_by_category|meal_type",
    ],
)
async def tg_process_restaurant_filters_states_handler(
    update: Update, state_data: dict
):
    filter_name = update.message.text[2::]

    if state_data["state"] == "find_restaurant|find_by_category|food_type":
        filters_state = state_data["food_filters_state"]
        state_data["filter_state"] = await process_filters_state(
            filters_state, filter_name, update
        )
        await update_tg_cache_state(update.message.from_.id, state_data)
    elif state_data["state"] == "find_restaurant|find_by_category|restaurant_type":
        filters_state = state_data["restaurant_filters_state"]
        state_data["filter_state"] = await process_filters_state(
            filters_state, filter_name, update
        )
        await update_tg_cache_state(update.message.from_.id, state_data)
    elif state_data["state"] == "find_restaurant|find_by_category|meal_type":
        filters_state = state_data["meal_filters_state"]
        state_data["filter_state"] = await process_filters_state(
            filters_state, filter_name, update
        )
        await update_tg_cache_state(update.message.from_.id, state_data)


@tg_dispatcher.register_handler(
    callback_query_func=lambda update: update.callback_query.data.startswith(
        "show_more"
    ),
    state_data_func=lambda state_data: state_data["state"]
    in [
        "find_restaurant|find_by_category|showing_restaurants",
        "find_restaurant|find_by_category|favorites",
    ],
)
async def tg_show_more_restaurants_handler(update: Update, state_data: dict):
    await edit_message_reply_markup(
        chat_id=update.callback_query.from_.id,
        message_id=update.callback_query.message.message_id,
        reply_markup=get_in_favorite_inline_keyboard(
            update.callback_query.data.split()[2], []
        ),
    )
    db = await get_db()
    if not state_data["state"] == "find_restaurant|find_by_category|favorites":
        restaurants = await Restaurants.get_restaurants_using_searching_filters(
            db,
            filters=state_data["restaurant_filters_state"]
            + state_data["food_filters_state"]
            + state_data["meal_filters_state"],
        )
    else:
        restaurants = await Restaurants.get_user_favorites_restaurants(
            db, str(update.callback_query.from_.id)
        )
    last_restaurant_index = int(update.callback_query.data.split()[1])
    last_elem_index = await show_5_of_restaurants(
        restaurants,
        last_restaurant_index,
        chat_id=update.callback_query.from_.id,
    )
    state_data["last_restaurant_index"] = last_elem_index
    await update_tg_cache_state(update.callback_query.from_.id, state_data)


@tg_dispatcher.register_handler(
    callback_query_func=lambda update: update.callback_query.data.startswith(
        "out_of_favorites"
    )
    or update.callback_query.data.startswith("in_favorites"),
    state_data_func=lambda state_data: state_data["state"]
    in [
        "find_restaurant|find_by_category|showing_restaurants",
        "find_restaurant|find_by_category|favorites",
    ],
)
async def tg_process_restaurant_favorite_state_handler(
    update: Update, state_data: dict
):
    restaurant_id = update.callback_query.data.split()[1]
    has_show_more = update.callback_query.data.split()[2]

    if update.callback_query.data.startswith("in_favorites"):
        db = await get_db()
        favorites = await Restaurants.add_restaurant_to_favorites(
            db, restaurant_id, str(update.callback_query.from_.id)
        )

    else:
        db = await get_db()
        favorites = await Restaurants.remove_restaurant_from_favorites(
            db, restaurant_id, str(update.callback_query.from_.id)
        )
        if state_data["state"] == "find_restaurant|find_by_category|favorites":
            await delete_message(
                chat_id=update.callback_query.from_.id,
                message_id=update.callback_query.message.message_id,
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
    await edit_message_reply_markup(
        update.callback_query.from_.id,
        update.callback_query.message.message_id,
        reply_markup=keyboard,
    )
