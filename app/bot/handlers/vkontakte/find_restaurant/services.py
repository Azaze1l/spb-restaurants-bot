from typing import List


from app.bot.messages.vkontakte import (
    get_in_favorite_inline_keyboard,
    get_restaurant_info_message_text,
    get_positive_filters_state_message,
    get_negative_filters_state_message,
    get_choose_type_of_parameter_in_restaurant_keyboard,
)
from app.cache.vk import get_photo_by_link
from app.db import get_db
from app.db.restaurants import Restaurants
from app.helpers.vkontakte import send_message
from app.schemas.vkontakte.outgoing import Message


async def process_filters_state(filters_state, filter_name, event):
    for filter_frame in filters_state:
        if filter_frame["name"] == filter_name:
            filter_frame["value"] = not filter_frame["value"]
            if event.objects.message.text[0] == "◼":
                msg = await get_positive_filters_state_message(
                    int(event.objects.message.from_id), filter_name
                )
                msg.keyboard = (
                    await get_choose_type_of_parameter_in_restaurant_keyboard(
                        filters_state
                    )
                )
                await send_message(msg)
            else:
                msg = await get_negative_filters_state_message(
                    int(event.objects.message.from_id), filter_name
                )
                msg.keyboard = (
                    await get_choose_type_of_parameter_in_restaurant_keyboard(
                        filters_state
                    )
                )
                await send_message(msg)
    return filters_state


async def show_5_of_restaurants(
    restaurants: List[dict], last_restaurant_index, user_id
):
    show_more = False

    db = await get_db()
    user_favorites_restaurants = await Restaurants.get_user_favorites_restaurants(
        db, str(user_id)
    )
    if len(restaurants) > 5 and len(restaurants) - last_restaurant_index > 5:
        show_more = True
    try:
        for i in range(last_restaurant_index, last_restaurant_index + 5):
            picture = restaurants[i].get("picture")
            if i == last_restaurant_index + 4 and show_more is True:
                keyboard = get_in_favorite_inline_keyboard(
                    str(restaurants[i]["_id"]),
                    [str(i["_id"]) for i in user_favorites_restaurants],
                    last_restaurant_index,
                    len(restaurants),
                    show_more=True,
                )
            else:
                keyboard = get_in_favorite_inline_keyboard(
                    str(restaurants[i]["_id"]),
                    [str(i["_id"]) for i in user_favorites_restaurants],
                    last_restaurant_index,
                    len(restaurants),
                    show_more=False,
                )
            if picture:
                attachment = await get_photo_by_link(picture)
                await send_message(
                    Message(
                        user_id=user_id,
                        attachment=attachment,
                        keyboard=keyboard,
                        message=get_restaurant_info_message_text(restaurants[i]),
                    )
                )
            else:
                await send_message(
                    Message(
                        user_id=user_id,
                        keyboard=keyboard,
                        message=get_restaurant_info_message_text(restaurants[i]),
                    )
                )
        return last_restaurant_index + 5
    except IndexError:
        return
