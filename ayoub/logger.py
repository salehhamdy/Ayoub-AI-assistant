"""
ayoub/logger.py — Centralised logging for Ayoub-AI-assistant.

Replaces the bash log.sh from hereiz.
Uses Python's standard logging with RotatingFileHandler.
"""
import logging
from logging.handlers import RotatingFileHandler
from ayoub.config import LOG_FILE, LOGS_DIR


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger backed by a rotating file at logs/ayoub.log.
    Max size: 200 KB, keeps 2 backups.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(
            str(LOG_FILE),
            maxBytes=200 * 1024,   # 200 KB
            backupCount=2,
            encoding="utf-8",
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] - %(message)s")
        )
        logger.addHandler(handler)

    return logger
