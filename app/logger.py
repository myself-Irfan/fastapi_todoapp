import logging
from logging.handlers import TimedRotatingFileHandler
import os

from app.config import settings

os.makedirs(settings.log_dir, exist_ok=True)


def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(funcName)s | %(message)s'
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