from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase

collection = "regions"


class CityDistricts:
    @staticmethod
    async def delete_many(db: AsyncIOMotorDatabase):
        db[collection].delete_many({})

    @staticmethod
    async def insert_many(db: AsyncIOMotorDatabase, data: List):
        db[collection].insert_many(data)

    @staticmethod
    async def get_list(db: AsyncIOMotorDatabase):
        cursor = db[collection].find({})
        service_centers_list = await cursor.to_list(None)
        return service_centers_list

    @staticmethod
    async def get_district_by_current_coords(
        db: AsyncIOMotorDatabase, lon: float, lat: float
    ):

        cursor = db[collection].find(
            {
                "geometry": {
                    "$geoIntersects": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [lon, lat],
                        },
                    }
                },
            }
        )
        district = await cursor.to_list(None)
        return district
