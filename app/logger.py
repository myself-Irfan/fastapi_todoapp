import os
import logging
import structlog
from logging.handlers import TimedRotatingFileHandler
import inspect

from app.config import settings


# ensure log directory exists
os.makedirs(settings.log_dir, exist_ok=True)

# ------------- LOGGER CONFIGURATION FUNCTION -------------
def configure_logger():
    """
    configure structlog with standard logging handlers (console + file)
    """
    log_level_name = settings.log_level.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    # standard logging setup
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(),
            TimedRotatingFileHandler(
                filename=f"{settings.log_dir}/{settings.log_file}",
                when="midnight",
                interval=1,
                backupCount=7,
                encoding='utf-8',
                utc=False
            )
        ]
    )

    # structlog setup
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso", utc=False),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False
    )

# ------------- LOGGER CREATION FUNCTION -------------
def get_logger(name: str = None):
    """
    return a structlog logger bound with module name
    """
    if name is None:
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'app')

    return structlog.get_logger(name)