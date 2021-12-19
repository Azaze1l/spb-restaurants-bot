import os
import secrets
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    DOMAIN: str = ""
    TG_BOT_USERNAME: str = ""
    VK_GROUP_USERNAME: str = ""

    SECRET_KEY: str = secrets.token_urlsafe(32)
    DEFAULT_ADMIN_LOGIN: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    MONGO_DB: str = "spb-bot"
    MONGODB_CONNECTION_URL: str = "mongodb+srv://places_spb:E34SBxaaz4qJ2PQ@places.cekmy.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE"

    ACCESS_TOKEN_EXPIRATION_TIME: int = 5 * 24 * 60 * 60  # 5 days

    LOG_INCOMING_EVENTS: bool = True

    TG_TOKEN: str = "1340132763:AAGmsEMlWk95dyVsbiZOphpbcdJT4xD7QSI"
    VK_TOKEN: str = ""

    VK_API_VERSION: str = "5.87"
    VK_CONFIRMATION_TOKEN: str = ""
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: str = ""

    NEAREST_RESTAURANTS_RADIUS = 3 * 1000  # радиус ближайших ресторанов (в метрах)

    TYPE_OF_RESTAURANT_FILTERS: List[dict] = [
        {"name": "Кафе", "pk": "type_of_restaurant.cafe", "value": False},
        {"name": "Ресторан", "pk": "type_of_restaurant.restaurant", "value": False},
        {"name": "Бар", "pk": "type_of_restaurant.bar", "value": False},
        {"name": "Магазин", "pk": "type_of_restaurant.shop", "value": False},
    ]

    TYPE_OF_MEAL_FILTERS: List[dict] = [
        {"name": "Завтрак", "pk": "type_of_meal.breakfast", "value": False},
        {"name": "Обед", "pk": "type_of_meal.lunch", "value": False},
        {"name": "Ужин", "pk": "type_of_meal.dinner", "value": False},
    ]

    TYPE_OF_FOOD_FILTERS: List[dict] = [
        {"name": "Европейская кухня", "pk": "type_of_food.european", "value": False},
        {"name": "Авторская кухня", "pk": "type_of_food.authors", "value": False},
        {"name": "Итальянская кухня", "pk": "type_of_food.italian", "value": False},
        {"name": "Азиатская кухня", "pk": "type_of_food.asian", "value": False},
        {
            "name": "Вегетарианская кухня",
            "pk": "type_of_food.vegetarian",
            "value": False,
        },
        {"name": "Японская кухня", "pk": "type_of_food.japan", "value": False},
    ]

    class Config:
        case_sensitive = True


settings = Settings()
