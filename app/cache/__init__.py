import json
import logging

import aioredis
from aioredis import Redis

from app.config import settings

logger = logging.getLogger("events")


class RedisCache:
    redis: Redis

    async def set_cache(self, cache_key, data):
        await self.redis.set(cache_key, json.dumps(data))

    async def get_cache(self, cache_key):
        raw_data = await self.redis.get(cache_key)
        if raw_data:
            return json.loads(raw_data.decode("utf-8"))
        return None

    async def change_cache_value(self, cache_key, key, value):
        raw_data = await self.redis.get(cache_key)
        if raw_data:
            data = json.loads(raw_data.decode("utf-8"))
            data[key] = value
            await self.redis.set(cache_key, json.dumps(data))
            return data
        return None

    async def get_cache_value(self, cache_key, key):
        raw_data = await self.redis.get(cache_key)
        if raw_data:
            data = json.loads(raw_data.decode("utf-8"))
            return data.get(key)
        return None


state_cache = RedisCache()


async def connect_cache():
    logger.info("Connecting to Redis")
    if settings.REDIS_PASSWORD:
        state_cache.redis = await aioredis.create_redis_pool(
            settings.REDIS_URL, password=settings.REDIS_PASSWORD
        )
    else:
        state_cache.redis = await aioredis.create_redis_pool(settings.REDIS_URL)
    logger.info("Connected to Redis")


async def disconnect_cache():
    logger.info("Disconnecting from Redis")
    state_cache.redis.close()
    await state_cache.redis.wait_closed()


async def update_tg_cache_state(data_key, state_data):
    state_data_key = f"tg:{data_key}"
    state_cache_service = get_state_cache()
    await state_cache_service.set_cache(state_data_key, state_data)


async def update_vk_cache_state(data_key, state_data):
    state_data_key = f"vk:{data_key}"
    state_cache_service = get_state_cache()
    await state_cache_service.set_cache(state_data_key, state_data)


def get_state_cache():
    return state_cache
