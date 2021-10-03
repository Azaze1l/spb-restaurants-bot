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

