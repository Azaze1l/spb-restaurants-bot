import datetime
import logging
from typing import Optional, List

import bson
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

logger = logging.getLogger("events")


collection = "users"


class Users(object):
    @staticmethod
    async def get_user_by_id(db: AsyncIOMotorDatabase, id: str) -> Optional[dict]:
        try:
            user = await db[collection].find_one({"_id": ObjectId(id)})
        except bson.errors.InvalidId:
            user = await db[collection].find_one({"user_id": id})
        except PyMongoError as ex:
            logger.error(f"get_user_by_id failed: {ex}")
            return None
        return user

    @staticmethod
    async def get_user_by_platform_id(
        db: AsyncIOMotorDatabase,
        user_id: str,
        platform: str,
    ) -> Optional[dict]:
        try:
            user = await db[collection].find_one(
                {
                    "user_id": user_id,
                    "platform": platform,
                }
            )
        except PyMongoError as ex:
            logger.error(f"get_user_by_platform_id failed: {ex}")
            return None
        return user

    @staticmethod
    async def register_bot_user(
        db: AsyncIOMotorDatabase,
        user_id: str,
        platform: str,
        ref_id: Optional[str] = None,
    ) -> Optional[str]:
        data = {
            "user_id": user_id,
            "platform": platform,
            "registered_at": datetime.datetime.now(datetime.timezone.utc),
            "ref_id": ref_id,
        }
        try:
            result = await db[collection].insert_one(data)
            logger.info(
                f"User {user_id} was successfully registered (platform={platform})"
            )
        except PyMongoError as ex:
            logger.error(f"register_bot_user failed: {ex}")
            return None
        return result.inserted_id

    @staticmethod
    async def get_or_create_user(
        db: AsyncIOMotorDatabase,
        user_id: str,
        platform: str,
        ref_id: Optional[str] = None,
    ) -> Optional[dict]:
        user = await Users.get_user_by_platform_id(
            db, user_id=user_id, platform=platform
        )
        if not user:
            new_id = await Users.register_bot_user(
                db, user_id=user_id, platform=platform, ref_id=ref_id
            )
            user = await Users.get_user_by_id(db, id=new_id)
        return user
