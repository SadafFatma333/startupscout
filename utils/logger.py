import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, level=logging.INFO):
    """Return a configured, structured logger with optional file rotation."""
    logger = logging.getLogger(name)
    if logger.handlers:  # avoid duplicates in reloads
        return logger

    # --- Formatter ---
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # --- Console handler (always on) ---
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # --- File handler (prod mode only) ---
    if os.getenv("ENV", "dev").lower() == "prod":
        os.makedirs("logs", exist_ok=True)
        file_handler = RotatingFileHandler(
            "logs/app.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # --- Log level ---
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    logger.propagate = False
    return logger

def sampled_log(logger, level: str, message: str, every: int = 10, index: int = 0):
    """
    Log every Nth message only — useful for high-frequency loops.
    Example:
        for i in range(1000):
            sampled_log(logger, "info", f"Processing item {i}", every=20, index=i)
    """
    if index % every == 0:
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(message)
