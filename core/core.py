#!/usr/bin/env python3

""" core.py contains core functionality for the application to run """

from core import config

import logging
#import yaml
import sys
import os

logger = logging.getLogger("logger")

class ApplicationCore(object):
    """Central class that is responsible for the environment setup, etc."""

    def __init__(self):
        super(ApplicationCore, self).__init__()

        # Prepare everything needed by the application.
        self.path=os.getcwd()
        self._prepareEnvironment()
        self._loadConfiguration()

    def _prepareEnvironment(self):
        """internal: _prepareEnvironment prepares the workspace of the app"""
        # Check for the main working directory
        dirs = [config.DATADIR, config.PAGEDIR, config.IMAGEDIR]
        for dir in dirs:
            if not os.path.exists(os.path.join(self.path, dir)):
                logger.info(f"creating working directory {dir}")
                os.makedirs(os.path.join(self.path, dir), 0o750) # Create directory and set permissions

    def _loadConfiguration(self):
        if not os.path.exists(os.path.join(self.path, config.CONFIGDIR)):
            logger.info(f"creating working directory {config.CONFIGDIR}")
            os.makedirs(os.path.join(self.path, config.CONFIGDIR), 0o750) # Create directory and set permissions
            
        if not os.path.exists(os.path.join(self.path, config.CONFIGDIR, config.CONFIG)):#f"{self.path+config.STREAMLIT}/{config.CONFIG}"):
            logger.critical(
                f"no configuration file found in {os.path.join(self.path, config.CONFIGDIR, config.CONFIG)}"
            )
            sys.exit(1)
        #with open(self.config_file, "r") as f:
        #    self.config = yaml.safe_load(f)


