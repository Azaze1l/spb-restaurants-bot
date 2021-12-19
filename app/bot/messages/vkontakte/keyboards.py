import json
from typing import Optional, List

from app.bot.messages import interface_controller, check_for_modifying
from app.schemas.vkontakte.outgoing import (
    Message,
    KeyboardAction,
    KeyboardButton,
    Keyboard,
)


def format_button(label: str, payload: str) -> KeyboardButton:
    button_payload = json.dumps({"button": f"{payload}"})
    button_action = KeyboardAction(
        type="text", label=f"{label}", payload=button_payload
    )
    return KeyboardButton(action=button_action)


def get_searching_filter_keyboard(current_filters_state) -> List:
    reply_keyboard = []

    for current_filter in current_filters_state:
        if current_filter["value"] is False:
            text = f"◼️{current_filter['name']}"
        else:
            text = f"◽️{current_filter['name']}"
        filter_button = format_button(text, "change_filters")
        reply_keyboard.append([filter_button])
    return reply_keyboard


@interface_controller.register_modifiable_object(
    dict(title="Кнопка для возвращения в главное меню", name="to_main_menu_button"),
    dict(title="Кнопка для отката назад", name="step_back_button"),
    title="Клавиатура для отката на шаг назад/возвращения в главное меню",
    platform="vk",
)
async def get_step_back_keyboard(modifiable=None):
    text = await check_for_modifying("step_back_button", modifiable, "⬅️ Назад")
    step_back_button = format_button(text, "back")
    text = await check_for_modifying(
        "to_main_menu_button", modifiable, "↩️ В главное меню"
    )
    to_main_menu_button = format_button(text, "to_main_menu")
    keyboard = Keyboard(
        buttons=[
            [step_back_button],
            [
                to_main_menu_button,
            ],
        ]
    )
    return keyboard


@interface_controller.register_modifiable_object(
    dict(
        title="Кнопка начала сценария поиска ресторана", name="find_restaurant_button"
    ),
    title="Клавиатура главного меню",
    platform="vk",
)
async def get_main_keyboard(modifiable=None):
    text = await check_for_modifying(
        "find_restaurant_button", modifiable, "🔎 Где ресторан"
    )
    find_restaurant_button = format_button(text, "find_restaurant")
    keyboard = Keyboard(
        buttons=[
            [find_restaurant_button],
        ]
    )
    return keyboard


@interface_controller.register_modifiable_object(
    dict(
        title="Кнопка начала сценария поиска ресторана по категориям",
        name="find_by_list_of_proposed_button",
    ),
    dict(
        title="Кнопка начала сценария поиска ресторана по местоположению",
        name="find_by_location_button",
    ),
    dict(
        title="Кнопка показа избранных ресторанов",
        name="show_favorite_restaurants_button",
    ),
    title="Клавиатура меню поиска ресторана",
    platform="vk",
)
async def get_find_restaurant_keyboard(modifiable=None):
    text = await check_for_modifying(
        "find_by_list_of_proposed_button", modifiable, "📖 Найти по категориям"
    )
    find_by_list_of_proposed_button = format_button(text, "by_list_of_proposed")
    text = await check_for_modifying(
        "find_by_location_button", modifiable, "📍Найти по местоположению"
    )
    find_by_location_button = format_button(text, "by_location")
    text = await check_for_modifying(
        "show_favorite_restaurants_button", modifiable, "✨ Избранное"
    )
    show_favorite_restaurants_button = format_button(text, "favorites")
    text = await check_for_modifying(
        "to_main_menu_button", modifiable, "↩️ В главное меню"
    )
    to_main_menu_button = format_button(text, "to_main_menu")
    keyboard = Keyboard(
        buttons=[
            [find_by_list_of_proposed_button],
            [find_by_location_button],
            [show_favorite_restaurants_button],
            [to_main_menu_button],
        ]
    )
    return keyboard


async def get_choose_type_of_parameter_in_restaurant_keyboard(
    parameter_filters_state: List[dict],
):
    food_types_buttons = get_searching_filter_keyboard(parameter_filters_state)
    back_button = format_button("⬅️ Назад", "back")
    next_button = format_button("➡️Далее", "next")
    keyboard = Keyboard(buttons=food_types_buttons + [[back_button, next_button]])

    return keyboard


@interface_controller.register_modifiable_object(
    dict(
        title="Кнопка показа следующих элементов в списке",
        name="show_more_button",
    ),
    title="Клавиатура показа следующих элементов",
    platform="vk",
)
async def get_show_more_keyboard(
    last_elem_index: int, count_of_elems: int, modifiable=None
):
    text = f"⬇️Показать еще {last_elem_index + 5}/{count_of_elems}"
    show_more_button = format_button(text, "show_more")
    text = await check_for_modifying("step_back_button", modifiable, "⬅️ Назад")
    step_back_button = format_button(text, "back")
    text = await check_for_modifying(
        "to_main_menu_button", modifiable, "↩️ В главное меню"
    )
    to_main_menu_button = format_button(text, "to_main_menu")

    keyboard = Keyboard(
        buttons=[
            [show_more_button],
            [step_back_button],
            [to_main_menu_button],
        ]
    )
    return keyboard


def get_in_favorite_inline_keyboard(
    restaurant_id,
    user_favorites,
    last_elem_index=None,
    count_of_elems=None,
    show_more=False,
):

    if restaurant_id in user_favorites:
        callback_data = f"out_of_favorites {restaurant_id} {1 if show_more else 0}"
        in_favorites_button = format_button("В избранном 🌟", callback_data)
        favorites_button = in_favorites_button
    else:
        callback_data = f"in_favorites {restaurant_id} {1 if show_more else 0}"
        in_favorites_button = format_button("В избранном 🌟", callback_data)
        favorites_button = in_favorites_button
    if show_more:
        text = f"⬇️Показать еще {last_elem_index + 5}/{count_of_elems}"
        callback_data = f"show_more {last_elem_index + 5} {restaurant_id}"
        show_more_button = format_button(text, callback_data)
        inline_keyboard = [[favorites_button], [show_more_button]]
    else:
        inline_keyboard = [[favorites_button]]
    keyboard = Keyboard(buttons=inline_keyboard, inline=True)
    return keyboard


@interface_controller.register_modifiable_object(
    dict(
        title="Кнопка поиска ресторанов в текущем районе",
        name="find_restaurants_in_neighborhood_button",
    ),
    dict(
        title="Кнопка поиска ближайших ресторанов",
        name="find_nearest_restaurants_button",
    ),
    title="Клавиатура поиска ресторана по локации",
    platform="vk",
)
async def get_find_restaurant_by_location_keyboard(
    modifiable=None,
):
    text = await check_for_modifying(
        "find_restaurants_in_neighborhood_button",
        modifiable,
        "🪧 Найти в текущем районе",
    )
    find_restaurants_in_neighborhood_button = format_button(text, "by_district")
    text = await check_for_modifying(
        "find_nearest_restaurants_button", modifiable, "📍 Найти ближайшие рестораны"
    )
    find_nearest_restaurants_button = format_button(text, "by_nearest")
    text = await check_for_modifying("step_back_button", modifiable, "⬅️ Назад")
    step_back_button = format_button(text, "back")
    text = await check_for_modifying(
        "to_main_menu_button", modifiable, "↩️ В главное меню"
    )
    to_main_menu_button = format_button(text, "to_main_menu")
    keyboard = Keyboard(
        buttons=[
            [find_restaurants_in_neighborhood_button],
            [find_nearest_restaurants_button],
            [step_back_button],
            [to_main_menu_button],
        ]
    )
    return keyboard


@interface_controller.register_modifiable_object(
    dict(title="Кнопка отправки локации", name="location_button"),
    title="Клавиатура отправления локации",
    platform="vk",
)
async def get_waiting_for_location_keyboard(modifiable=True):
    location_payload = json.dumps({"button": "location"})
    location_action = KeyboardAction(
        type="location",
        payload=location_payload,
    )
    location_button = KeyboardButton(action=location_action)

    text = await check_for_modifying("step_back_button", modifiable, "⬅️ Назад")
    step_back_button = format_button(text, "back")
    text = await check_for_modifying(
        "to_main_menu_button", modifiable, "↩️ В главное меню"
    )
    to_main_menu_button = format_button(text, "to_main_menu")
    keyboard = Keyboard(
        buttons=[
            [location_button],
            [step_back_button],
            [to_main_menu_button],
        ]
    )
    return keyboard
