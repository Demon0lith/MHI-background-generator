""" globals.py initializes global (singleton) values/instances for the project """

import logging
import sys

# Global variables
logger: logging.Logger = None
defaultLoglevel = logging.DEBUG

def _setup_logging():
    """_setup_logging() sets up the logging infrastructure for the application"""
    global logger
    logger = logging.getLogger("logger")
    logger.setLevel(defaultLoglevel)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stdlog = logging.StreamHandler(stream=sys.stderr)
    stdlog.setLevel(defaultLoglevel)
    stdlog.setFormatter(formatter)
    logger.addHandler(stdlog)

def setup():
    """setup() prepares the global environment for the application"""
    _setup_logging()