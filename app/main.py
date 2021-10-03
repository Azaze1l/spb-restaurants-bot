import logging.config

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api import api_router
from app.bot.messages import interface_controller
from app.cache import connect_cache, disconnect_cache
from app.config import settings
from app.db import connect_to_mongodb, close_mongodb_connection
from app.helpers.telegram import set_webhook_on_startup

log_conf = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(process)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": "DEBUG",
        }
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
    "loggers": {
        "gunicorn": {"propagate": True},
        "uvicorn": {"propagate": True},
        "uvicorn.access": {"propagate": True},
        "events": {"propagate": True},
        "tasks": {"propagate": True},
    },
}
logging.config.dictConfig(log_conf)

app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_event_handler("startup", connect_to_mongodb)
app.add_event_handler("startup", connect_cache)
app.add_event_handler("startup", set_webhook_on_startup)
app.add_event_handler("startup", interface_controller.fill_db_interface_collection)
app.add_event_handler("shutdown", close_mongodb_connection)
app.add_event_handler("shutdown", disconnect_cache)

app.include_router(api_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"{settings.DOMAIN}",
        "localhost",
        "localhost:3000",
        "http://localhost:3000",
        "http://localhost",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
