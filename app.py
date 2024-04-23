#!/usr/bin/env python3

""" file contains the logic for running the app """
from core import globals
from core.core import ApplicationCore
from core.application import Application

import logging
import argparse

globals.setup()
logger = logging.getLogger("logger")

def main():
    """ streamlit run app.py -- --config ./streamlit/config.toml """
    
    lpParser = argparse.ArgumentParser()

    # Parse arguments
    lpParser.add_argument(
        "-c",
        "--config",
        help="Configuration file",
        default="",
    )
    
    lpArgs = lpParser.parse_args()
    try:
        if len(lpArgs.target_file) == 0:
            logger.warning("No configuration file specified")
    except AttributeError:
        pass

    # Initialize and execute the application
    #logger.info("[+] Core initializing")
    appCore = ApplicationCore()

    #logger.info("[+] Application launching")
    app = Application(appCore)
    app.run()


if __name__ == "__main__":
    main()