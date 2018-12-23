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

from os.path import expanduser
from functools import wraps

LOGGER = logging.getLogger('typitlearn')

LOG_FORMAT = '%(asctime)s :: %(levelname)-5s :: %(message)s'

def logmethod(func):
    """Decorator for setting up the logger in LoggingMixin subclasses."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.is_log_enabled:
            return None

        args = list(args)
        msg = '{parent_class!s}{nvim_id} :: {msg!s}'
        args[0] = msg.format(nvim_id=f' ({self.nvid})' if self.nvid else '',
                             parent_class=type(self).__name__,
                             msg=args[0])
        return func(self, *args, **kwargs)
    return wrapper


class LoggingMixin:
    """Class that adds logging functions to a subclass."""
    is_log_enabled = False
    nvid = None
    _logger = LOGGER

    def _setup_log(self, log_file, log_level, nvim_id):

        try:
            self._logger.setLevel(getattr(logging, log_level.upper()))
            log_file = expanduser(log_file)
        except AttributeError:
            self._logger.setLevel(logging.INFO)
        except TypeError:
            return

        formatter = logging.Formatter(LOG_FORMAT)
        file_handler = RotatingFileHandler(log_file, 'a', 1000000, 1)

        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
        LoggingMixin.is_log_enabled = True
        LoggingMixin.nvid = nvim_id

        self.info(f'Initialize for {nvim_id}')

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
