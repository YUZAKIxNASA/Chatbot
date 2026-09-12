"""Minimal application logging without user message contents."""

import logging


def get_logger() -> logging.Logger:
    logger = logging.getLogger("chatbot")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
