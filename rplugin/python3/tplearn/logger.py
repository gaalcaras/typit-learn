# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: logger.py
Author: Gabriel Alcaras
Original script by: Tommy Allen <tommy at esdf.io>
License: GNU GPL v3
"""

import logging
from logging.handlers import RotatingFileHandler
from functools import wraps

LOGGER = logging.getLogger('typitlearn')

LOG_FORMAT = '%(asctime)s :: %(levelname)-5s :: %(message)s'
LOG_FILE = 'typeitlearn.log'

def setup():
    LOGGER.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = RotatingFileHandler(LOG_FILE, 'a', 1000000, 1)

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    LOGGER.addHandler(file_handler)

def logmethod(func):
    """Decorator for setting up the logger in LoggingMixin subclasses."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.is_log_enabled:
            return
        return func(self, *args, **kwargs)
    return wrapper


class LoggingMixin(object):
    """Class that adds logging functions to a subclass."""

    is_log_enabled = False
    _logger = LOGGER

    @logmethod
    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    @logmethod
    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    @logmethod
    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)
    warn = warning

    @logmethod
    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)
