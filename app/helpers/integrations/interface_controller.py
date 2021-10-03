import functools
import logging
from typing import List

import bson
import datetime

from app.config import settings
from app.db import get_db, logger
from app.db.interface_objects import InterfaceObjects


async def update_data_in_collection(data: List[dict], db):
    prev_data = await InterfaceObjects.get_all_objects(db)
    logger.info('Collection "interface_objects" is waiting for update with a new data')
    for obj in prev_data:
        if not (
            (obj["object"], obj["platform"])
            in [(item["object"], item["platform"]) for item in data]
        ):
            await InterfaceObjects.delete_one_object(db, obj)

    if len(prev_data) == 0:
        await InterfaceObjects.insert_many_objects(db, data)
        return
    for obj in data:
        await InterfaceObjects.update_object_with_basic_changes(db, obj, prev_data)


async def get_modifiable_reply_or_button(f, platform):
    object_name = str(f).split()[1]
    db = await get_db()
    reply_or_button = await InterfaceObjects.get_modifiable_reply_or_button(
        db, object_name, platform
    )
    return reply_or_button


class InterfaceController:
    def __init__(self):
        self.__interface_objects = []

    def register_modifiable_object(self, *args, title=None, platform=None):
        def wrapper(f):
            if args:
                buttons = []
                for button in args:
                    buttons.append(
                        dict(
                            _id=bson.ObjectId(),
                            object=button.get("name"),
                            type="button",
                            text=None,
                            title=button.get("title"),
                            platform=platform,
                            created_at=datetime.datetime.now(),
                            updated_at=None,
                        )
                    )
                self.__interface_objects.append(
                    dict(
                        object=str(f).split()[1],
                        type="keyboard",
                        title=title,
                        platform=platform,
                        created_at=datetime.datetime.now(),
                        updated_at=None,
                        buttons=buttons,
                    ),
                )
            else:
                self.__interface_objects.append(
                    dict(
                        object=str(f).split()[1],
                        type="reply",
                        text=None,
                        title=title,
                        platform=platform,
                        created_at=datetime.datetime.now(),
                        updated_at=None,
                    )
                )

            async def inner_func(*f_args, **f_kwargs):
                modifiable = await get_modifiable_reply_or_button(f, platform)
                result = await f(*f_args, **f_kwargs, modifiable=modifiable)
                return result

            return inner_func

        return wrapper

    async def fill_db_interface_collection(self):
        db = await get_db()
        await update_data_in_collection(self.__interface_objects, db)
