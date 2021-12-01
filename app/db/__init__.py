import logging

from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus as quote

from app.config import settings
from app.db.admins import Admins

logger = logging.getLogger("events")


class Database:
    client: AsyncIOMotorClient


db = Database()


async def connect_to_mongodb():
    logger.info("Connecting to MongoDB")
    db.client = AsyncIOMotorClient(
        settings.MONGODB_CONNECTION_URL,
        serverSelectionTimeoutMS=10,
    )
    await db.client[settings.MONGO_DB]["restaurants"].create_index(
        [("location", "2dsphere")]
    )
    # server_info = await db.client.server_info()
    logger.info("Obtained MongoDB connection")
    logger.info("Checking default users")
    await Admins.check_default_admin(db.client[settings.MONGO_DB])
    logger.info("All DB specific procedures completed")


async def close_mongodb_connection():
    logger.info("Closing MongoDB connections")
    db.client.close()


async def get_db():
    return db.client[settings.MONGO_DB]


async def get_mongo_client():
    return db.client
