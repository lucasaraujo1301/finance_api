import logging.config

from modules.core.config import settings

log_level = "WARNING" if settings.ENVIRONMENT == "test" else settings.LOG_LEVEL

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation_id": {
                "()": "asgi_correlation_id.CorrelationIdFilter",
                "uuid_length": 32,
                "default_value": "-",
            },
        },
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.json.JsonFormatter",
                "format": "%(asctime)s %(correlation_id)s %(name)s %(levelname)s %(message)s %(exc_info)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "filters": ["correlation_id"],
                "formatter": "json",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }
)

logger = logging.getLogger("finance_api")
