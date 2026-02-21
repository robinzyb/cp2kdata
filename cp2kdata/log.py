import logging
import os

_LOGGER_NAME = "cp2kdata"

level_name = os.environ.get("CP2KDATA_LOG_LEVEL", "INFO")
level = logging._nameToLevel.get(level_name, logging.INFO)

# format to include timestamp and module
if level_name == "DEBUG":
    _formatter = logging.Formatter(
        "CP2KDATA| %(asctime)s - %(levelname)-8s %(name)-40s: %(message)s"
    )
else:
    _formatter = logging.Formatter("CP2KDATA| %(message)s")

_logger = logging.getLogger(_LOGGER_NAME)
_logger.setLevel(level)
_logger.propagate = True

# Only attach a handler when the root logger has no handlers.
# This keeps standalone behavior without changing global logging config.
if not logging.getLogger().handlers and not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setLevel(level)
    _handler.setFormatter(_formatter)
    _logger.addHandler(_handler)

# suppress transitions logging
# logging.getLogger('transitions.core').setLevel(logging.WARNING)


def get_logger(name=None):
    if name:
        return logging.getLogger(f"{_LOGGER_NAME}.{name}")
    return _logger
