import logging
import sys

from pythonjsonlogger import jsonlogger

from app.core.config import settings


def setup_logging() -> None:
    # Get root logger
    root_logger = logging.getLogger()

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Standard output stream handler
    console_handler = logging.StreamHandler(sys.stdout)

    if settings.APP_ENV == "production":
        # Structured JSON logs in production
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(filename)s %(lineno)d %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ"
        )
    else:
        # Easy-to-read console logs in development
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)s in %(name)s (%(filename)s:%(lineno)d): %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set logging level based on debug setting
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    root_logger.setLevel(log_level)

    # Suppress verbose dependency logs in development
    logging.getLogger("uvicorn.access").setLevel(logging.INFO if settings.DEBUG else logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    logging.info(f"Logging initialized in {settings.APP_ENV} mode.")


def get_logger(name: str = "app") -> logging.Logger:
    """Return a logger instance for the given module name."""
    return logging.getLogger(name)

