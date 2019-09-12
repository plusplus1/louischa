#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import logging

import requests
from lxml import etree

_logger = logging.getLogger(__name__)


class BaseCrawler(object):
    """
        base crawler
    """

    def __init__(self, session=None, logger=None):
        self._session = session or requests.session()
        self.logger = logger or _logger

    def request(self, url):
        resp = self._session.get(url)
        return Response(resp.status_code, resp.text)

    @abc.abstractmethod
    def run(self, **kwargs):
        pass

    pass


class Response(object):
    def __init__(self, code, text):
        self.code = code
        self.text = text
        self._etree = None

    @property
    def etree(self):
        if self._etree is None:
            self._etree = etree.HTML(self.text)
        return self._etree


pass
