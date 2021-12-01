import datetime
import logging
from typing import Optional, Union, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError
from bson import ObjectId

logger = logging.getLogger("events")


collection = "interface_objects"


def _fill_id_without_underscore(interface_objects: Union[dict, List[dict]]):
    """
    Функция переименовывает поле _id в id
    """
    try:
        interface_objects["id"] = str(interface_objects.pop("_id"))
        try:
            for button in interface_objects["buttons"]:
                button["id"] = str(button.pop("_id"))
            return interface_objects
        except KeyError:
            return interface_objects
    except Exception:  # если возникает ошибка, значит был передан список модифицируемых объектов
        for interface_object in interface_objects:
            interface_object["id"] = str(interface_object.pop("_id"))
            try:
                for button in interface_object["buttons"]:
                    button["id"] = str(button.pop("_id"))
            except KeyError:
                pass
        return interface_objects


class InterfaceObjects:
    @staticmethod
    async def get_object_by_id(
        db: AsyncIOMotorDatabase, _id: ObjectId
    ) -> Optional[dict]:
        """
        Метод возвращает объект по его ObjectId
        """
        try:
            object_info = await db[collection].find_one({"_id": _id})
            if object_info is None:
                keyboards = await InterfaceObjects.get_elements_by_type(db, "keyboard")
                buttons = []
                for keyboard in keyboards:
                    buttons += keyboard["buttons"]
                button = [button for button in buttons if button["_id"] == _id]
                return button[0]
        except PyMongoError as ex:
            logger.error(f"get_object_by_id failed: {ex}")
            return None
        except IndexError:
            return None
        return object_info

    @staticmethod
    async def get_elements_by_type(
        db: AsyncIOMotorDatabase, object_type: str
    ) -> Optional[list]:
        """
        Метод возвращает объекты по указанному type
        type: keyboard, platform, reply
        """
        try:
            if object_type == "button":
                keyboards = await InterfaceObjects.get_elements_by_type(db, "keyboard")
                buttons = []
                for keyboard in keyboards:
                    buttons += keyboard["buttons"]
                return buttons
            else:
                cursor = db[collection].find({"type": object_type})
                objects_info = await cursor.to_list(None)
        except PyMongoError as ex:
            logger.error(f"get_object_by_id failed: {ex}")
            return None
        return objects_info

    @staticmethod
    async def get_element_by_type_and_platform(
        db: AsyncIOMotorDatabase, object_type: str, platform: str
    ):
        """
        Метод возвращает объекты по указанным type и platform
        type: keyboard, platform, reply
        platform: vk, tg
        """
        mongo_find_method_filter = {}
        if object_type is not None:
            mongo_find_method_filter.update({"type": object_type})
        if platform is not None:
            mongo_find_method_filter.update({"platform": platform})
        if object_type == "button":
            buttons = await InterfaceObjects.get_elements_by_type(db, "button")
            if platform is None:
                return buttons
            else:
                buttons = [
                    button for button in buttons if button["platform"] == platform
                ]
                return buttons
        else:
            cursor = db[collection].find(mongo_find_method_filter)
            objects_info = await cursor.to_list(None)
            return objects_info

    @staticmethod
    async def get_interface_object(
        db: AsyncIOMotorDatabase, object_name: str, platform: str = None
    ) -> Union[Optional[dict], list]:
        """
        Метод возвращает InterfaceObject по указанным object_name и platform;
        Если platform не указана, возвращает список объектов для обеих платформ
        platform: vk, tg
        """
        try:
            if object_name.endswith("button"):
                keyboards = await InterfaceObjects.get_elements_by_type(db, "keyboard")
                buttons = []
                for keyboard in keyboards:
                    if object_name in [
                        button["object"] for button in keyboard["buttons"]
                    ]:
                        index = [
                            button["object"] for button in keyboard["buttons"]
                        ].index(object_name)
                        buttons.append(keyboard["buttons"][index])
                if platform:
                    for button in buttons:
                        if button["platform"] == platform:
                            return button
                return buttons
            else:
                if platform:
                    object_info = await db[collection].find_one(
                        {"object": object_name, "platform": platform}
                    )
                    return object_info
                else:
                    cursor = db[collection].find({"object": object_name})
                    objects_info = await cursor.to_list(None)
                    return objects_info
        except PyMongoError as ex:
            logger.error(f"get_object_by_id failed: {ex}")
            return None

    @staticmethod
    async def update_interface_object_by_id(
        db: AsyncIOMotorDatabase, _id: ObjectId, text: str
    ):
        """
        Метод обновляет текст объекта интерфейса по его _ID
        """
        elem = await db[collection].find_one_and_update(
            {"_id": _id, "text": {"$exists": True}},
            {"$set": {"text": text, "updated_at": datetime.datetime.now()}},
        )
        if elem is not None:
            if text:
                logger.info(f"Object with id {str(_id)} was updated with text: {text}")
            else:
                logger.info(f"Object with id {str(_id)} was updated with default text")
            return elem
        else:
            elem = await db[collection].find_one_and_update(
                {"buttons._id": _id},
                {
                    "$set": {
                        "buttons.$.text": text,
                        "buttons.$.updated_at": datetime.datetime.now(),
                    }
                },
            )
            if text:
                logger.info(f"Object with id {str(_id)} was updated with text: {text}")
            else:
                logger.info(f"Object with id {str(_id)} was updated with default text")
            return elem

    @staticmethod
    async def update_interface_object_by_name(
        db: AsyncIOMotorDatabase, object_name: str, platform: str, text: str
    ):
        """
        Метод обновляет текст объекта интерфейса по его object_name и platform
        """
        elem = await db[collection].find_one_and_update(
            {"object": object_name, "text": {"$exists": True}},
            {"$set": {"text": text, "updated_at": datetime.datetime.now()}},
        )
        if elem is not None:
            if text:
                logger.info(
                    f"Object with name '{object_name}' and platform '{platform}' was updated with text: '{text}'"
                )
            else:
                logger.info(
                    f"Object with name '{object_name}' and platform '{platform}' was updated with default text"
                )
            return elem
        else:
            elem = await db[collection].find_one_and_update(
                {"buttons.platform": platform, "buttons.object": object_name},
                {
                    "$set": {
                        "buttons.$.text": text,
                        "buttons.$.updated_at": datetime.datetime.now(),
                    }
                },
            )
            if text:
                logger.info(
                    f"Object with name '{object_name}' and platform '{platform}' was updated with text: '{text}'"
                )
            else:
                logger.info(
                    f"Object with name '{object_name}' and platform '{platform}' was updated with default text"
                )
            return elem

    @staticmethod
    async def get_modifiable_reply_or_button(
        db: AsyncIOMotorDatabase, object_name: str, platform: str
    ):
        """
        Метод возвращает модифицированный текст для определнного хэндлера
        (необходимо для исправной работы хэндлеров tg)
        """
        m_object = await db[collection].find_one(
            {"object": object_name, "platform": platform}
        )
        if object_name.endswith("keyboard"):
            back_step_buttons = await db[collection].find_one(
                {"object": "get_step_back_keyboard"}
            )
            return m_object["buttons"] + back_step_buttons["buttons"]
        else:
            return m_object["text"]

    @staticmethod
    async def get_all_objects(db: AsyncIOMotorDatabase):
        """
        Метод возвращает все элементы в коллекц
        """
        cursor = db[collection].find({})
        objects = await cursor.to_list(None)
        return objects

    @staticmethod
    async def insert_one_object(db: AsyncIOMotorDatabase, interface_object: dict):
        """
        Метод добавляет элемент в коллекцию
        """
        await db[collection].insert_one(interface_object)

    @staticmethod
    async def delete_one_object(db: AsyncIOMotorDatabase, interface_object: dict):
        """
        Метод удаляет элемент из коллекции
        """
        await db[collection].delete_one(interface_object)

    @staticmethod
    async def insert_many_objects(
        db: AsyncIOMotorDatabase, interface_objects: List[dict]
    ):
        """
        Метод добавляет элементы в коллекцию
        """
        db[collection].insert_many(interface_objects)

    @staticmethod
    async def update_object_with_basic_changes(
        db: AsyncIOMotorDatabase, interface_object, prev_data
    ):
        """
        Метод обанвляет базовую конфигурацию элемнта, например для reply
        это обновление title, а для keyboard - title и изменения в кнопках
        """
        try:
            if interface_object["object"] in [item["object"] for item in prev_data]:
                index = [item["object"] for item in prev_data].index(
                    interface_object["object"]
                )

                interface_object["text"] = prev_data[index]["text"]
                if (
                    interface_object["title"] != prev_data[index]["title"]
                    and interface_object["platform"] == prev_data[index]["platform"]
                ):
                    elem = await db[collection].find_one_and_update(
                        {
                            "object": interface_object["object"],
                            "platform": interface_object["platform"],
                        },
                        {
                            "$set": {
                                "title": interface_object["title"],
                            }
                        },
                    )
                    if elem is None:
                        await InterfaceObjects.insert_one_object(db, interface_object)
            else:
                await InterfaceObjects.insert_one_object(db, interface_object)
        except KeyError:  # Если у объекта нет 'text' -> это клавиатура
            index = [{item["object"], item["platform"]} for item in prev_data].index(
                {interface_object["object"], interface_object["platform"]}
            )
            prev_buttons = prev_data[index]["buttons"]
            for button in interface_object["buttons"]:
                try:
                    index = [item["object"] for item in prev_buttons].index(
                        button["object"]
                    )
                    button["_id"] = prev_buttons[index]["_id"]
                    button["text"] = prev_buttons[index]["text"]
                    button["updated_at"] = prev_buttons[index]["updated_at"]
                except ValueError:
                    pass
            elem = await db[collection].find_one_and_update(
                {
                    "object": interface_object["object"],
                    "platform": interface_object["platform"],
                },
                {
                    "$set": {
                        "title": interface_object["title"],
                        "buttons": interface_object["buttons"],
                    }
                },
            )
            if elem is None:
                await InterfaceObjects.insert_one_object(db, interface_object)

        except ValueError:
            pass
