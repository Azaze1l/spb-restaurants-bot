from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.helpers.auth import get_password_hash

collection = "admins"


class Admins(object):
    @staticmethod
    async def get_default_admin(db: AsyncIOMotorDatabase, login: str) -> Optional[dict]:
        admin = await db[collection].find_one({"login": login})
        return admin

    @staticmethod
    async def get_admin_by_id(db: AsyncIOMotorDatabase, admin_id: str) -> Optional[dict]:
        admin = await db[collection].find_one({"_id": ObjectId(admin_id)})
        return admin

    @staticmethod
    async def create_default_user(
        db: AsyncIOMotorDatabase, login: str, password: str
    ) -> bool:
        password_hash = get_password_hash(password)
        _ = await db[collection].insert_one(
            {"login": login, "password_hash": password_hash}
        )
        return True

    @staticmethod
    async def check_default_admin(db: AsyncIOMotorDatabase):
        default_admin = await Admins.get_default_admin(
            db, login=settings.DEFAULT_ADMIN_LOGIN
        )
        if not default_admin:
            _ = await Admins.create_default_user(
                db,
                login=settings.DEFAULT_ADMIN_LOGIN,
                password=settings.DEFAULT_ADMIN_PASSWORD,
            )
