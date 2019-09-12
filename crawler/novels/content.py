#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import re

import config.db
import crawler.base


class ContentCrawler(crawler.base.BaseCrawler):
    """ crawl novel content """

    _pattern = re.compile('adsbygoogle\s*=\s*window.adsbygoogle\s*\|\|\s*\[\]\).push\(\{\}\);\s*</script>\s*'
                          '(<p>.*</p>)'
                          '\s*<script async src=',
                          re.RegexFlag.S)

    def _save(self, title, ver, catalog, body):
        c = config.db.connect()
        now = datetime.datetime.now().astimezone(config.tz_local)
        id(now)
        id(c)

        pass

    def run(self, **kwargs):
        title = kwargs['title']
        ver = kwargs['ver']
        catalog = kwargs['catalog']

        url = catalog['url']
        resp = self.request(url)
        self._save(title, ver, catalog, resp)

        text = resp.text

        m = self._pattern.search(text)
        return m.group(1)

    pass
