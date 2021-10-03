from fastapi import APIRouter

from app.api.auth import auth_router
from app.api.bot import bot_router
from app.api.interface import interface_objects_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(bot_router, prefix="/bot", tags=["bot"])
api_router.include_router(
    interface_objects_router, prefix="/interface_objects", tags=["interface"]
)

