import logging
import sys
from logging.config import dictConfig

from app.core.config import settings


def setup_logging():
    LOG_LEVEL = settings.log_level.upper()

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            },
            "detailed": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "detailed" if LOG_LEVEL == "DEBUG" else "default",
            },
        },

        "loggers": {
            "uvicorn": {
                "level": LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
        },

        "root": {
            "level": LOG_LEVEL,
            "handlers": ["console"],
        },
    })


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)