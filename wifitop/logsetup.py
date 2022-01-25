"""setup logging"""
# vim: tw=100 foldmethod=indent
# pylint: disable=invalid-name, superfluous-parens
# pylint: disable=redefined-outer-name, logging-not-lazy, logging-format-interpolation
# pylint: disable=missing-docstring, trailing-whitespace, trailing-newlines, too-few-public-methods

import logging
from logging.handlers import RotatingFileHandler

from wifitop.parse_args import args

# logger = logging.getLogger(__name__)
logger = logging.getLogger("")  # => This is the key to allow logging from other modules


class PathTruncatingFormatter(logging.Formatter):
    """formatter for logging"""

    def format(self, record):
        pathname = record.pathname
        if len(pathname) > 23:
            pathname = "...{}".format(pathname[-19:])
        record.pathname = pathname
        return super(PathTruncatingFormatter, self).format(record)


def setup_logging():
    """setup logging"""

    formatter = logging.Formatter("[%(asctime)s]%(levelname)8s - %(message)s")

    if args.debug:
        args.loglevel = "DEBUG"
        formatter = PathTruncatingFormatter(
            "[%(asctime)s] {%(pathname)23s:%(lineno)-3d}%(levelname)8s - %(message)s"
        )

    handler = RotatingFileHandler(args.logfile, maxBytes=10 ** 6, backupCount=2)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(args.loglevel)
    logger.info("------------------------------------- new start -----------------")

    # turn off werkzeug logging:
    werkzeug_log = logging.getLogger("werkzeug")
    werkzeug_log.setLevel(logging.CRITICAL)
    werkzeug_log.addHandler(handler)

    # turn off sqlalchemy logging:
    sqlalchemy_log = logging.getLogger("sqlalchemy.engine.base.Engine")
    sqlalchemy_log.setLevel(logging.CRITICAL)
    sqlalchemy_log.addHandler(handler)
    return logger


logger = setup_logging()
