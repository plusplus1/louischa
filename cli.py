#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import sys

import click
import requests

logging.basicConfig(format='%(levelname)s\t%(asctime)s\t%(thread)d\t%(message)s',
                    datefmt='[%d/%b/%Y %H:%M:%S]',
                    level=logging.INFO,
                    stream=sys.stdout, )


@click.group()
@click.pass_context
def cli(ctx):
    """金庸小说爬取"""
    import config.log
    logger = config.log.Logger("logs/crawler.log").logger
    ctx.obj = dict(session=requests.session(), logger=logger)
    return ctx


@cli.command()
@click.pass_context
def index(ctx):
    """获取小说列表"""
    from crawler.novels.index import IndexCrawler
    result = IndexCrawler(**ctx.obj).run()
    for r in result:
        print(r)
    return


@cli.command()
@click.option('--title', '-t', default='', help='小说名称')
@click.option('--ver', '-v', default='修订版', help='版本', show_default=True)
@click.option('--reversed', '-r', is_flag=True, help='是否逆序排列')
@click.option('--skip', '-s', is_flag=True, help='是否跳过已经存在的')
@click.pass_context
def catalog(ctx, **kwargs):
    """更新小说目录"""
    filter_dict = {k: v for k, v in kwargs.items() if v and k in ['title', 'ver']}
    import config.db
    c = config.db.connect()
    books = [b for b in c.find(filter_dict, ['title', 'ver', 'url', 'catalog'])]
    if not books:
        logging.warning("没有符合条件的小说，请更新小说列表")
        exit(-1)

    do_reverse = kwargs['reversed']
    do_skip = kwargs['skip']

    from crawler.novels.catalogue import CatalogueCrawler
    crawler = CatalogueCrawler(**ctx.obj)

    def _dump_catalog(logs):

        for r in logs:
            print(u'\t%-40s%s' % (r['title'], r['url']))

        return

    for b in books:
        print('===> 开始处理', b['title'], b['ver'], b['url'])
        if 'catalog' in b and b['catalog'] and do_skip:
            _dump_catalog(b['catalog'])
            print("----\t 已处理直接跳过, 找到{}个章节".format(len(b['catalog'])))
            print()
            continue

        result = crawler.run(book=b, reverse=do_reverse)
        _dump_catalog(result)
        print("----\t 处理成功, 找到{}个章节".format(len(result)))
        print()


if __name__ == '__main__':
    cli()

pass

pass
