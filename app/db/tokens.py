from motor.motor_asyncio import AsyncIOMotorDatabase

collection = "tokens"


class Tokens(object):
    @staticmethod
    async def add_invalidated_token(db: AsyncIOMotorDatabase, token: str, user_id: str):
        token_data = await db[collection].find_one({"token": token, "user_id": user_id})
        if not token_data:
            _ = await db[collection].insert_one(
                {"token": token, "user_id": user_id}
            )
        return True

    @staticmethod
    async def check_user_token(db: AsyncIOMotorDatabase, token: str, user_id: str):
        token_data = await db[collection].find_one({"token": token, "user_id": user_id})
        return token_data
