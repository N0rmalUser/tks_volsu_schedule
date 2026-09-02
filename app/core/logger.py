import logging
from datetime import datetime

from app.core.config import config
from app.core.constants import TZ


def set_logging(logger: str):
    logging.Formatter.converter = lambda *args: datetime.now(TZ).timetuple()
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "FATAL": logging.FATAL,
        "EXCEPTION": logging.ERROR,
    }
    logging.basicConfig(
        level=levels[config.logging_level],
        format="%(asctime)s %(levelname)s [%(funcName)s] %(message)s",
        datefmt="%H:%M:%S %d-%m-%Y",
        handlers=[logging.StreamHandler()],
        force=True,
    )
    logging.getLogger(logger).setLevel(levels[config.logging_level])
