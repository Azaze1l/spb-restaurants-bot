import logging
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

logger = logging.getLogger("events")


collection = "restaurants"


class Restaurants:
    pass
