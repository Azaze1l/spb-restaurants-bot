import asyncio
import types

from app.bot.messages import check_for_modified_text
from app.schemas.telegram.incoming import Update


class TelegramDispatcher(object):
    def __init__(self):
        self.__handlers = []
        self.__default_handler = None

    def register_handler(
        self,
        message_func=None,
        callback_query_func=None,
        state_data_func=None,
    ):
        def wrapper(f):
            self.__handlers.append(
                (
                    message_func,
                    callback_query_func,
                    state_data_func,
                    f,
                )
            )

        return wrapper

    def default_handler(self):
        def wrapper(f):
            self.__default_handler = f

        return wrapper

    async def process_event(self, event: Update, state_data: dict, modifiable_items):
        for (
            message_func,
            callback_query_func,
            state_data_func,
            handler,
        ) in self.__handlers:
            state_data_func_result = None
            if state_data_func is not None:
                state_data_func_result = state_data_func(state_data)

            message_func_result = None
            if message_func is not None:
                message_func_result = False
                if event.message is not None:
                    if message_func is not None:
                        try:
                            try:
                                button_text = await check_for_modified_text(
                                    *message_func(), modifiable_items
                                )
                                message_func_result = event.message.text.startswith(
                                    button_text
                                )
                            except TypeError:
                                message_func_result = message_func(event)
                        except Exception:
                            pass
            callback_query_func_result = None
            if callback_query_func is not None:
                callback_query_func_result = False
                if event.callback_query is not None:
                    callback_query_func_result = callback_query_func(event)

            event_result = {
                state_data_func_result,
                message_func_result,
                callback_query_func_result,
            }
            event_result.remove(None)
            try:
                summary_result = event_result.pop()
                for result in event_result:
                    summary_result *= result
                if summary_result:
                    await handler(event, state_data)
                    return
            except KeyError:
                pass
        if self.__default_handler is not None:
            await self.__default_handler(event, state_data)
