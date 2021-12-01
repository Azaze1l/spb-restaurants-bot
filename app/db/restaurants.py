import logging
from typing import Optional, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.db import db
from app.db.users import Users

logger = logging.getLogger("events")


collection = "restaurants"


class Restaurants:
    @staticmethod
    async def delete_many(db: AsyncIOMotorDatabase):
        db[collection].delete_many({})

    @staticmethod
    async def insert_many(db: AsyncIOMotorDatabase, data: List):
        db[collection].insert_many(data)

    @staticmethod
    async def get_list(db: AsyncIOMotorDatabase):
        cursor = db[collection].find({})
        restaurants_list = await cursor.to_list(None)
        return restaurants_list

    @staticmethod
    async def get_restaurants_using_searching_filters(
        db: AsyncIOMotorDatabase, filters: List[dict]
    ):
        valid_filters = []
        for item in filters:
            if item["value"] is True:
                valid_filters.append(item["pk"])
        cursor = db[collection].find({k: True for k in valid_filters})
        restaurants = await cursor.to_list(None)
        return restaurants

    @staticmethod
    async def add_restaurant_to_favorites(
        db: AsyncIOMotorDatabase, restaurant_id, user_id
    ):
        favorites = await Restaurants.get_user_favorites_restaurants(db, user_id)
        favorites = [str(i["_id"]) for i in favorites]
        favorites.append(restaurant_id)

        from app.db.users import collection

        await db[collection].find_one_and_update(
            {"user_id": user_id}, {"$set": {"favorites": favorites}}
        )
        return favorites

    @staticmethod
    async def remove_restaurant_from_favorites(
        db: AsyncIOMotorDatabase, restaurant_id, user_id
    ):
        favorites = await Restaurants.get_user_favorites_restaurants(db, user_id)
        favorites = [str(i["_id"]) for i in favorites]
        favorites.remove(restaurant_id)

        from app.db.users import collection

        await db[collection].find_one_and_update(
            {"user_id": user_id}, {"$set": {"favorites": favorites}}
        )
        return favorites

    @staticmethod
    async def get_user_favorites_restaurants(db: AsyncIOMotorDatabase, user_id):
        user = await Users.get_user_by_id(db, user_id)
        favorites = user.get("favorites")

        find_mongo_state = {}
        if favorites:
            for favorite_id in favorites:
                find_mongo_state.update({"_id": ObjectId(favorite_id)})

            cursor = db[collection].find(find_mongo_state)
            favorites = await cursor.to_list(None)
            return favorites
        return []

    @staticmethod
    async def get_nearest_restaurants(db: AsyncIOMotorDatabase, lon, lat):
        cursor = db[collection].find(
            {
                "location": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [lon, lat],
                        },
                        "$maxDistance": settings.NEAREST_RESTAURANTS_RADIUS,
                    }
                }
            }
        )
        return await cursor.to_list(None)

    @staticmethod
    async def get_restaurants_by_district_name(db: AsyncIOMotorDatabase, district_name):
        cursor = db[collection].find({"district": district_name})
        return await cursor.to_list(None)
