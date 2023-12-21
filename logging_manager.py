import logging
from datetime import datetime

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    green = "\x1b[1;32m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    light_blue = "\x1b[1;36m"
    purple = "\x1b[1;35m"
    blue = "\x1b[1;34m"
    blink_red = "\x1b[5m\x1b[1;31m"
    reset = "\x1b[0m"
    format = '%(asctime)s [%(levelname)s] %(name)s -  %(message)s'

    FORMATS = {
        logging.DEBUG: purple + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def initialize_logger():
    format = '%(asctime)s [%(levelname)s]  %(message)s'
    log_file_name = "latest.log"
    #logging.getLogger("discord").setLevel(logging.WARNING)
    #logging.getLogger("requests").setLevel(logging.WARNING)
    #logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.basicConfig(filename=log_file_name, format=format, level=logging.DEBUG)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)

    console.setFormatter(CustomFormatter())
    logging.getLogger('').addHandler(console)
    logging.info("logger initialised!")