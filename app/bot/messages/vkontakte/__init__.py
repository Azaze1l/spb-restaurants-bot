from typing import List

from app.bot.messages import interface_controller
from app.bot.messages.telegram import _get_message_text
from app.bot.messages.vkontakte.keyboards import *


@interface_controller.register_modifiable_object(
    title="Стартовое сообщение", platform="vk"
)
async def get_start_message(user_id: int, modifiable=None) -> Message:
    default_message = (
        "Привет, я - чат-бот Бургер Кинг! Я помогу тебе найти ближайши ресторан, ознакомиться с меню и "
        "сделать заказ.\nЧто же ты ждёшь? Воспользуйся скорее кнопками в моём меню ⬇️"
    )
    msg = Message(
        user_id=user_id,
        message=_get_message_text(modifiable, default_message),
    )
    msg.keyboard = await get_main_keyboard()
    return msg


@interface_controller.register_modifiable_object(
    title="Дефолтное сообщение", platform="vk"
)
async def get_default_message(user_id: int, modifiable=None) -> Message:
    default_message = "Я бы рад вам помочь, но пока не понимаю такие сообщения :(\nПожалуйста, выберите пункт меню ⬇️"
    msg = Message(
        user_id=user_id, message=_get_message_text(modifiable, default_message)
    )
    msg.keyboard = await get_main_keyboard()
    return msg


@interface_controller.register_modifiable_object(
    title="Сообщение о возврате в главное меню ", platform="vk"
)
async def get_back_to_main_menu_message(user_id: int, modifiable=None) -> Message:
    msg = Message(
        user_id=user_id,
        message=_get_message_text(modifiable, "Возвращаюсь в главное меню"),
    )
    msg.keyboard = await get_main_keyboard()
    return msg


@interface_controller.register_modifiable_object(
    title="Сообщение о начале сценария поиска ресторанов", platform="vk"
)
async def get_find_restaurant_message(user_id: int, modifiable=None) -> Message:
    msg = Message(
        user_id=user_id,
        message=_get_message_text(
            modifiable, "Выберите удобный вам способ поиска ресторана))"
        ),
    )
    msg.keyboard = await get_find_restaurant_keyboard()
    return msg


@interface_controller.register_modifiable_object(
    title="Сообщение о выборе желаемой кухни", platform="vk"
)
async def get_choose_type_of_food_message(
    user_id: int, food_filters_state: List, modifiable=None
) -> Message:
    msg = Message(
        user_id=user_id,
        message=_get_message_text(
            modifiable,
            "Блюда какой кухни вас интересуют сегодня? (Если вас не интересует что-то особенное вы можете просто "
            "нажать кнопку 'Далее')",
        ),
    )
    msg.keyboard = await get_choose_type_of_parameter_in_restaurant_keyboard(
        parameter_filters_state=food_filters_state
    )
    return msg


@interface_controller.register_modifiable_object(
    title="Сообщение о выборе типа искомого заведения", platform="vk"
)
async def get_choose_type_of_restaurant_message(
    user_id: int, restaurant_filters_state: List, modifiable=None
) -> Message:
    msg = Message(
        user_id=user_id,
        message=_get_message_text(
            modifiable,
            "Заведение какого типа вы ищете?",
        ),
    )
    msg.keyboard = await get_choose_type_of_parameter_in_restaurant_keyboard(
        parameter_filters_state=restaurant_filters_state
    )
    return msg


@interface_controller.register_modifiable_object(
    title="Сообщение о выборе типа приема пищи (завтрак, обед, ужин....)", platform="vk"
)
async def get_choose_type_of_meal_message(
    user_id: int, meal_filters_state: List, modifiable=None
) -> Message:
    msg = Message(
        user_id=user_id,
        message=_get_message_text(
            modifiable,
            "Хотите позавтракать/пообедать/поужинать в заведении?",
        ),
    )
    msg.keyboard = await get_choose_type_of_parameter_in_restaurant_keyboard(
        parameter_filters_state=meal_filters_state
    )
    return msg


@interface_controller.register_modifiable_object(
    title="Сообщение с информацией о том, что фильтр переключен в режим выкл.",
    platform="vk",
)
async def get_positive_filters_state_message(
    user_id: int, filters_name: str, modifiable=None
):
    default_msg_text = f'Окей, фильтр "{filters_name}" включен.'
    return Message(
        user_id=user_id,
        message=_get_message_text(modifiable, default_msg_text),
    )


@interface_controller.register_modifiable_object(
    title="Сообщение с информацией о том, что фильтр переключен в режим вкл.",
    platform="vk",
)
async def get_negative_filters_state_message(
    user_id: int, filters_name: str, modifiable=None
):
    default_msg_text = f'Окей,  фильтр "{filters_name}" выключен.'
    return Message(
        user_id=user_id,
        message=_get_message_text(modifiable, default_msg_text),
    )


def get_restaurant_info_message_text(restaurant):
    text = (
        f"*{restaurant.get('name')}*\n{restaurant.get('description')}\n\nСредняя цена: {restaurant.get('mean_prices')}"
        f"\nРайон: _{restaurant.get('neighborhood')}_ {restaurant.get('address')}\nВремя работы: {restaurant.get('time')}\n"
        f"Сайт: {restaurant.get('links')}"
    )
    return text


@interface_controller.register_modifiable_object(
    title="Сообщение о выборе опции поиска по локации", platform="vk"
)
async def get_find_restaurant_by_location_message(
    user_id: int, modifiable=None
) -> Message:
    msg = Message(
        user_id=user_id,
        message=_get_message_text(
            modifiable,
            "Перед тем как отправить локацию, выберите, хотите ли вы искать рестораны рядом с собой или же в своем районе?",
        ),
    )
    msg.keyboard = await get_find_restaurant_by_location_keyboard()
    return msg


@interface_controller.register_modifiable_object(
    title="Сообщение с запросом отправить локацию",
    platform="vk",
)
async def get_request_location_message(user_id: int, modifiable=None):
    default_msg_text = "Отправь мне свое местоположение 📍"
    return Message(
        user_id=user_id,
        message=_get_message_text(modifiable, default_msg_text),
    )
