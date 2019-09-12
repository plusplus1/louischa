#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import urllib.parse

import config.db
import crawler.base


class CatalogueCrawler(crawler.base.BaseCrawler):
    """ crawl novel catalogue """

    def _save(self, book, catalog):
        c = config.db.connect()
        up_ret = c.update_one({'_id': book['_id']}, {"$set": {
            "catalog"    : catalog,
            'update_time': datetime.datetime.now().astimezone(config.tz_local),
        }})
        self.logger.info('save catalog ok , book=%s, catalog_len=%s, update_re=%s', book, len(catalog),
                         up_ret.modified_count)
        pass

    def run(self, **kwargs):
        book = kwargs['book']
        reverse = kwargs['reverse']

        url = book['url']
        resp = self.request(url)
        catalog = []
        for one in resp.etree.xpath('//*[@id="pu_box"]/div[3]/ul/li'):
            title = str.strip(one.xpath('.//text()')[0]).replace('\u3000', ' ')
            link = urllib.parse.urljoin(url, one.xpath("./a/@href")[0])

            if reverse:
                catalog.insert(0, {'title': title, 'url': link})
            else:
                catalog.append({'title': title, 'url': link})

        self._save(book, catalog)
        return catalog
