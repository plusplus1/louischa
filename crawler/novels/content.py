#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import re

import config.db
import crawler.base


class ContentCrawler(crawler.base.BaseCrawler):
    """ crawl novel content """

    _pattern = re.compile('adsbygoogle\s*=\s*window.adsbygoogle\s*\|\|\s*\[\]\).push\(\{\}\);\s*</script>\s*'
                          '(<p>.*p>)'
                          '\s*<script async src=',
                          re.RegexFlag.S)

    def _save(self, title, ver, catalog, body):
        now = datetime.datetime.now().astimezone(config.tz_local)
        condition = dict(catalog_title=catalog['title'], catalog_url=catalog['url'],
                         title=title, ver=ver)
        doc = dict(body=body, update_time=now, length=len(body))
        doc.update(condition)
        c = config.db.connect_contents()
        up_result = c.update_one(condition, {"$set": doc}, upsert=True)
        self.logger.info("save content ok, condition= %s, content_len=%s, up_cnt=%s, insert_id=%s",
                         condition, len(body), up_result.modified_count, up_result.upserted_id)
        if up_result and up_result.upserted_id:
            return up_result.upserted_id

        record = c.find_one(condition, ['_id'])
        return record['_id']

    def run(self, **kwargs):
        title = kwargs['title']
        ver = kwargs['ver']
        catalog = kwargs['catalog']

        url = catalog['url']
        resp = self.request(url)

        text = resp.text

        m = self._pattern.search(text)
        body = m.group(1)
        body_id = self._save(title, ver, catalog, body)
        return body_id, len(body)

    pass
