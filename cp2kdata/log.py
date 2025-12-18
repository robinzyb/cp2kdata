import logging
import os

_LOGGER_NAME = "cp2kdata"

level_name = os.environ.get('CP2KDATA_LOG_LEVEL', 'INFO')
level = logging._nameToLevel.get(level_name, logging.INFO)

logger = logging.getLogger(_LOGGER_NAME)
logger.setLevel(level)
logger.propagate = False  # do NOT touch root logger

if not logger.handlers:
    handler = logging.StreamHandler()

    if level_name == "DEBUG":
        formatter = logging.Formatter(
            "CP2KDATA| %(asctime)s - %(levelname)-8s %(name)-40s: %(message)s"
        )
    else:
        formatter = logging.Formatter("CP2KDATA| %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger(name=None):
    if name:
        return logging.getLogger(f"{_LOGGER_NAME}.{name}")
    return logger
