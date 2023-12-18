import logging
import sys


class CustomFormatter(logging.Formatter):
    GREY = "\x1b[38;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: GREY,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED,
    }

    def __init__(self, *args, prefix_format="", **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix_format = prefix_format

    def format(self, record):
        log_fmt = (
            f"{self.FORMATS.get(record.levelno)}"
            f"{self.prefix_format}{self.RESET}"
        )
        if record.levelno >= logging.WARNING:
            log_fmt += " - (%(filename)s:%(lineno)d)"
        formatter = logging.Formatter(log_fmt, validate=False)
        return formatter.format(record)


def setup_logger(
    verbosity: str,
    logger_name: str,
    root_level_verbosity: str = "CRITICAL",
    prefix_format: str = "",
):
    handlers = [
        logging.StreamHandler(sys.stdout),
    ]
    # handlers[0].setFormatter(CustomFormatter(prefix_format=prefix_format))
    prefix_format = "%(asctime)s - %(levelname)8s: %(message)s"

    logging.basicConfig(
        handlers=handlers,
        format=prefix_format,  # for default
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level=getattr(logging, root_level_verbosity.upper()),
    )
    logger = logging.getLogger(logger_name)
    logger.setLevel(verbosity.upper())
