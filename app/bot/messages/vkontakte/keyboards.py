import json
from typing import Optional

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


@interface_controller.register_modifiable_object(
    dict(title="Кнопка перехода в меню", name="menu_button"),
    dict(
        title="Кнопка начала сценария оформления заказа", name="menu_make_order_button"
    ),
    dict(
        title="Кнопка начала сценария поиска ресторана", name="find_restaurant_button"
    ),
    title="Клавиатура главного меню",
    platform="vk",
)
async def get_main_keyboard(modifiable=None) -> Keyboard:
    text = await check_for_modifying(
        "menu_make_order_button", modifiable, "🛒 Оформить заказ"
    )
    make_order_button = format_button(text, "make_order")

    text = await check_for_modifying(
        "find_restaurant_button", modifiable, "🔎 Где ресторан"
    )
    find_restaurant_button = format_button(text, "find_restaurant")

    text = await check_for_modifying("menu_button", modifiable, "🍔 Меню")
    menu_button = format_button(text, "menu")

    buttons = [[make_order_button], [find_restaurant_button], [menu_button]]
    return Keyboard(buttons=buttons)
