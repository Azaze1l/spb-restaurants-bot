from app.db.interface_objects import InterfaceObjects
from app.helpers.integrations.interface_controller import InterfaceController
from app.db import get_db

interface_controller = InterfaceController()


async def check_for_modifying(item: str, modified_items, default_text):
    try:
        for obj in modified_items:
            if obj["object"] == item:
                text = obj["text"]

                if text is not None:
                    return text
                else:
                    return default_text
    except Exception:
        return default_text


async def check_for_modified_text(obj: str, default_text: str, modifiable_items) -> str:
    for keyboard in modifiable_items:
        for button in keyboard["buttons"]:
            if button["object"] == obj:
                if button["text"] is not None:
                    return button["text"]
                else:
                    return default_text


async def get_modifiable_items():
    db = await get_db()
    keyboards = await InterfaceObjects.get_elements_by_type(db, "keyboard")
    return keyboards
