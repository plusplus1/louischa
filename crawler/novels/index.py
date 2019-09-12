#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import urllib
import urllib.parse

from pymongo.results import UpdateResult

import config.db
import crawler.base


class IndexCrawler(crawler.base.BaseCrawler):
    """
    index 
    """

    def _save(self, item):
        c = config.db.connect()
        item['update_time'] = datetime.datetime.now().astimezone(config.tz_local)
        ret = c.update_one({'title': item['title'], 'ver': item['ver']}, {"$set": item}, upsert=True)
        if ret and isinstance(ret, UpdateResult):
            self.logger.info('save item ok, ret=%s , item = %s', (ret.modified_count, ret.upserted_id), item)

    def run(self, **kwargs):
        url = 'http://www.jinyongwang.com/book/'
        resp = self.request(url)

        # parse versions
        versions = resp.etree.xpath('//*[@id="qnav"]/ul/li/text()')
        index_data = [{'version': v, 'description': [], 'book_list': []} for v in versions]

        # parse descriptions
        descriptions_nodes = resp.etree.xpath('//*[@id="main"]/div[2]/h2')
        for i, dn in enumerate(descriptions_nodes):
            for x in dn.itertext():
                if x:
                    index_data[i]['description'].append(x)

        # parse book list
        book_list_nodes = resp.etree.xpath('//*[@id="main"]/div[2]/ul[@class="list"]')
        for i, bln in enumerate(book_list_nodes):
            lst = index_data[i]['book_list']
            for book_node in bln.xpath('./li'):
                info = dict()
                title = book_node.xpath("./p[2]//text()")[0]
                info['title'] = str.rstrip(title, '小说')
                info['url'] = urllib.parse.urljoin(url, book_node.xpath("./p[2]/a/@href")[0])
                info['cover'] = urllib.parse.urljoin(url, book_node.xpath("./p[1]/a/img/@src")[0])
                extra = [str.strip(x) for x in str.split(book_node.xpath("./p[3]//text()")[0], '/')]
                info['press'] = extra[0]
                info['year'] = extra[1]
                lst.append(info)

        result = []

        # dump index data
        for i, data in enumerate(index_data):
            for book in data['book_list']:
                item = dict()
                item['ver'] = data['version']
                item['desc'] = data['description']
                item.update(book)
                self._save(item)
                result.append("{ver} - {year} - {press} - {title}".format(**item))

        return result
