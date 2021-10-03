from app.bot.messages.telegram.keyboards import *


def _get_message_text(modifiable, default_text):
    if modifiable is not None:
        message_text = modifiable
    else:
        message_text = default_text
    return message_text


@interface_controller.register_modifiable_object(
    title="Стартовое сообщение", platform="tg"
)
async def get_start_message(chat_id: int, modifiable=None) -> Message:
    msg = Message(
        chat_id=chat_id,
        text=_get_message_text(
            modifiable,
            "Привет, я - чат-бот самых крутых чуваков! Я помогу тебе найти интересный ресторан или кафе"
            ".\nЧто же ты ждёшь? Воспользуйся скорее кнопками в моём меню ⬇️",
        ),
    )
    msg.reply_markup = await get_main_keyboard()
    return msg


@interface_controller.register_modifiable_object(
    title="Дефолтное сообщение", platform="tg"
)
async def get_default_message(chat_id: int, modifiable=None) -> Message:
    msg = Message(
        chat_id=chat_id,
        text=_get_message_text(
            modifiable,
            "Я бы рад вам помочь, но пока не понимаю такие сообщения :(\nПожалуйста, "
            "выберите пункт меню ⬇️",
        ),
    )
    return msg


@interface_controller.register_modifiable_object(
    title="Сообщение о возврате в главное меню ", platform="tg"
)
async def get_back_to_main_menu_message(chat_id: int, modifiable=None) -> Message:
    msg = Message(
        chat_id=chat_id,
        text=_get_message_text(modifiable, "Возвращаюсь в главное меню"),
    )
    msg.reply_markup = await get_main_keyboard()
    return msg
