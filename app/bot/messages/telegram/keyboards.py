from typing import Optional, List

from app.helpers.telegram import send_message
from app.schemas.telegram.outgoing import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from app.config import settings
from app.bot.messages import interface_controller, check_for_modifying


def get_searching_filter_keyboard(current_filters_state) -> List:
    reply_keyboard = []

    for current_filter in current_filters_state:
        if current_filter["value"] is False:
            text = f"◼️{current_filter['name']}"
        else:
            text = f"◽️{current_filter['name']}"
        filter_button = KeyboardButton(text=text)
        reply_keyboard.append([filter_button])
    return reply_keyboard


@interface_controller.register_modifiable_object(
    dict(title="Кнопка для возвращения в главное меню", name="to_main_menu_button"),
    dict(title="Кнопка для отката назад", name="step_back_button"),
    title="Клавиатура для отката на шаг назад/возвращения в главное меню",
    platform="tg",
)
async def get_step_back_keyboard(modifiable) -> ReplyKeyboardMarkup:
    step_back_button = KeyboardButton(
        text=await check_for_modifying("step_back_button", modifiable, "⬅️ Назад")
    )
    to_main_menu_button = KeyboardButton(
        text=await check_for_modifying(
            "to_main_menu_button", modifiable, "↩️ В главное меню"
        )
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [step_back_button],
            [to_main_menu_button],
        ]
    )
    return keyboard


@interface_controller.register_modifiable_object(
    dict(
        title="Кнопка начала сценария поиска ресторана", name="find_restaurant_button"
    ),
    title="Клавиатура главного меню",
    platform="tg",
)
async def get_main_keyboard(modifiable=None) -> ReplyKeyboardMarkup:
    find_restaurant_button = KeyboardButton(
        text=await check_for_modifying(
            "find_restaurant_button", modifiable, "🔎 Где ресторан"
        )
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
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
    dict(
        title="Кнопка выхода в главное меню",
        name="to_main_menu_button",
    ),
    title="Клавиатура меню поиска ресторана",
    platform="tg",
)
async def get_find_restaurant_keyboard(modifiable=None) -> ReplyKeyboardMarkup:
    find_by_list_of_proposed_button = KeyboardButton(
        text=await check_for_modifying(
            "find_by_list_of_proposed_button", modifiable, "📖 Найти по категориям"
        )
    )
    find_by_location_button = KeyboardButton(
        text=await check_for_modifying(
            "find_by_location_button", modifiable, "📍Найти по местоположению"
        )
    )
    show_favorite_restaurants_button = KeyboardButton(
        text=await check_for_modifying(
            "show_favorite_restaurants_button", modifiable, "✨ Избранное"
        )
    )
    to_main_menu_button = KeyboardButton(
        text=await check_for_modifying(
            "to_main_menu_button", modifiable, "↩️ В главное меню"
        )
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [find_by_list_of_proposed_button],
            [find_by_location_button],
            [show_favorite_restaurants_button],
            [to_main_menu_button],
        ]
    )
    return keyboard


async def get_choose_type_of_parameter_in_restaurant_keyboard(
    parameter_filters_state: List[dict],
) -> ReplyKeyboardMarkup:
    food_types_buttons = get_searching_filter_keyboard(parameter_filters_state)
    back_button = KeyboardButton(text="⬅️ Назад")
    next_button = KeyboardButton(text="➡️Далее")
    keyboard = ReplyKeyboardMarkup(
        keyboard=food_types_buttons + [[back_button, next_button]]
    )

    return keyboard


@interface_controller.register_modifiable_object(
    dict(
        title="Кнопка показа следующих элементов в списке",
        name="show_more_button",
    ),
    dict(title="Кнопка для возвращения в главное меню", name="to_main_menu_button"),
    title="Клавиатура показа следующих элементов",
    platform="tg",
)
async def get_show_more_keyboard(
    last_elem_index: int, count_of_elems: int, modifiable=None
) -> ReplyKeyboardMarkup:
    show_more_button = KeyboardButton(
        text=f"⬇️Показать еще {last_elem_index+5}/{count_of_elems}"
    )
    step_back_button = KeyboardButton(
        text=await check_for_modifying("step_back_button", modifiable, "⬅️ Назад")
    )
    to_main_menu_button = KeyboardButton(
        text=await check_for_modifying(
            "to_main_menu_button", modifiable, "↩️ В главное меню"
        )
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
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
        in_favorites_button = InlineKeyboardButton(
            text="В избранном 🌟",
            callback_data=f"out_of_favorites {restaurant_id} {1 if show_more else 0}",
        )
        favorites_button = in_favorites_button
    else:
        not_in_favorites_button = InlineKeyboardButton(
            text="В избранное ⭐️",
            callback_data=f"in_favorites {restaurant_id} {1 if show_more else 0}",
        )
        favorites_button = not_in_favorites_button
    if show_more:
        show_more_button = InlineKeyboardButton(
            text=f"⬇️Показать еще {last_elem_index + 5}/{count_of_elems}",
            callback_data=f"show_more {last_elem_index + 5} {restaurant_id}",
        )
        inline_keyboard = [[favorites_button], [show_more_button]]
    else:
        inline_keyboard = [[favorites_button]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
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
    platform="tg",
)
async def get_find_restaurant_by_location_keyboard(
    modifiable=None,
) -> ReplyKeyboardMarkup:
    find_restaurants_in_neighborhood_button = KeyboardButton(
        text=await check_for_modifying(
            "find_restaurants_in_neighborhood_button",
            modifiable,
            "🪧 Найти в текущем районе",
        )
    )
    find_nearest_restaurants_button = KeyboardButton(
        text=await check_for_modifying(
            "find_nearest_restaurants_button", modifiable, "📍 Найти ближайшие рестораны"
        )
    )
    step_back_button = KeyboardButton(
        text=await check_for_modifying("step_back_button", modifiable, "⬅️ Назад")
    )
    to_main_menu_button = KeyboardButton(
        text=await check_for_modifying(
            "to_main_menu_button", modifiable, "↩️ В главное меню"
        )
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
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
    platform="tg",
)
async def get_waiting_for_location_keyboard(modifiable=True) -> ReplyKeyboardMarkup:
    location_button = KeyboardButton(
        text=await check_for_modifying(
            "location_button", modifiable, "📍 Отправить локацию"
        ),
        request_location=True,
    )
    step_back_button = KeyboardButton(
        text=await check_for_modifying("step_back_button", modifiable, "⬅️ Назад")
    )
    to_main_menu_button = KeyboardButton(
        text=await check_for_modifying(
            "to_main_menu_button", modifiable, "↩️ В главное меню"
        )
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [location_button],
            [step_back_button],
            [to_main_menu_button],
        ]
    )
    return keyboard
