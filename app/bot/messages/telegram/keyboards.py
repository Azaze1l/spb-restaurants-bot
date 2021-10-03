from typing import Optional

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


@interface_controller.register_modifiable_object(
    dict(title="Кнопка перехода в меню", name="menu_button"),
    dict(
        title="Кнопка начала сценария оформления заказа", name="menu_make_order_button"
    ),
    dict(
        title="Кнопка начала сценария поиска ресторана", name="find_restaurant_button"
    ),
    title="Клавиатура главного меню",
    platform="tg",
)
async def get_main_keyboard(modifiable=None) -> ReplyKeyboardMarkup:
    menu_make_order_button = KeyboardButton(
        text=await check_for_modifying(
            "menu_make_order_button", modifiable, "🛒 Оформить заказ"
        )
    )
    find_restaurant_button = KeyboardButton(
        text=await check_for_modifying(
            "find_restaurant_button", modifiable, "🔎 Где ресторан"
        )
    )
    menu_button = KeyboardButton(
        text=await check_for_modifying("menu_button", modifiable, "🍔 Меню")
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [menu_make_order_button],
            [find_restaurant_button],
            [menu_button],
        ]
    )
    return keyboard


