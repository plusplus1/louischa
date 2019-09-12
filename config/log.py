#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from logging import handlers


class Logger(object):
    """Logger"""

    _level_relations = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING,
                        'error': logging.ERROR, }
    _default_fmt = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'

    def __init__(self, filename, level='info', when='D', back_count=3, fmt=None):
        self.logger = logging.getLogger(filename)
        self.logger.propagate = 0
        format_str = logging.Formatter(fmt or self._default_fmt)
        self.logger.setLevel(self._level_relations.get(level))
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=back_count,
                                               encoding='utf-8')
        th.setFormatter(format_str)
        self.logger.addHandler(th)

        #
        # sh = logging.StreamHandler()
        # sh.setFormatter(format_str)
        # self.logger.addHandler(sh)
        #
