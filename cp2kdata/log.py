import logging
import os

level_name = os.environ.get('CP2KDATA_LOG_LEVEL', 'INFO')
level = logging._nameToLevel.get(level_name, logging.INFO)

# format to include timestamp and module
logging.basicConfig(format='CP2KDATA| %(levelname)-8s %(name)-40s: %(message)s', level=level)
# suppress transitions logging
# logging.getLogger('transitions.core').setLevel(logging.WARNING)

def get_logger(name=None):
    return logging.getLogger(name)