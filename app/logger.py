import logging
from logging.handlers import TimedRotatingFileHandler
import os
from enum import StrEnum

from app.config import settings


# ------------- FORMATTERS -------------
LOG_FORMAT_DEBUG = "%(asctime)s | %(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"
LOG_FORMAT_DEFAULT = "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s | %(message)s"


# ------------- LOG LEVELS -------------
class LogLevels(StrEnum):
    debug = 'DEBUG'
    info = 'INFO'
    warning = 'WARNING'
    error = 'ERROR'


# ensure log directory exists
os.makedirs(settings.log_dir, exist_ok=True)


# ------------- LOGGER CREATION FUNCTION -------------
def get_logger(name: str = __name__) -> logging.Logger:
    """
    Returns a configured logger instance.
    Uses both console and timed rotating file handlers.
    :param name:
    :return:
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        LOG_FORMAT_DEFAULT, "%Y-%m-%d %H:%M:%S"
    )

    # console handling
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # file logging
    file_handler = TimedRotatingFileHandler(
        filename=f'{settings.log_dir}/{settings.log_file}',
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8',
        utc=False
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# ------------- LOGGER CONFIGURATION FUNCTION -------------
def configure_logger(log_level: str = LogLevels.error):
    """
    configure the logger with a specific log level and format.
    :param log_level:
    :return:
    """

    log_level = str(log_level).upper()
    valid_levels = [level.value for level in LogLevels]

    if log_level not in valid_levels:
        log_level = LogLevels.error.value

    if log_level == LogLevels.debug:
        logging.basicConfig(
            level=log_level,
            format=LOG_FORMAT_DEBUG,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        logging.basicConfig(
            level=log_level,
            format=LOG_FORMAT_DEFAULT,
            datefmt="%Y-%m-%d %H:%M:%S"
        )