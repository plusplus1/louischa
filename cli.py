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

    return


@cli.command()
@click.option('--title', '-t', required=True, type=click.STRING, help='小说名称')
@click.option('--ver', '-v', default='修订版', help='版本', show_default=True)
@click.option('--skip', '-s', is_flag=True, help='是否跳过已经存在的')
@click.pass_context
def body(ctx, **kwargs):
    """更新小说内容"""
    filter_dict = {k: v for k, v in kwargs.items() if v and k in ['title', 'ver']}
    import config.db
    c = config.db.connect()

    book_list = [b for b in c.find(filter_dict, ['title', 'ver', 'url', 'catalog'])]
    if not book_list:
        logging.warning("没有符合条件的小说，请更新小说列表")
        exit(-1)
    if len(book_list) > 1:
        logging.warning("存在多个版本的,请确认是否有误")
        exit(-1)

    book = book_list[0]
    do_skip = kwargs['skip']
    from crawler.novels.content import ContentCrawler
    crawler = ContentCrawler(**ctx.obj)

    title = book['title']
    ver = book['ver']
    catalog_lst = book['catalog']

    modified = False

    for catalog in catalog_lst:
        if catalog.get('body_id'):
            if do_skip:
                print("---> 跳过已处理的内容：", title, ver, catalog['title'], catalog['url'])
                print("\t--> body = ", catalog['body_id'], catalog['length'])
                continue

        body_id, body_length = crawler.run(title=title, ver=ver, catalog=catalog)
        catalog['body_id'] = str(body_id)
        catalog['length'] = body_length
        modified = True
        print("---> 正在处理：", title, ver, catalog['title'], catalog['url'])
        print("\t--> body = ", body_id, body_length)

    if modified:
        up_ret = c.update_one({'_id': book['_id']}, {"$set": {'catalog': catalog_lst}})
        if up_ret.modified_count > 0:
            print("\t\t--> save catalog ok")
    print()
    return


@cli.command()
@click.option('--ver', '-v', default='修订版', help='版本', show_default=True)
@click.pass_context
def list_book(ctx, **kwargs):
    """列出书籍列表"""
    import config.db

    c = config.db.connect()
    v_dict = dict()
    cursor = c.find(None, ['title', 'ver'])
    for row in cursor:
        if row['ver'] not in v_dict:
            v_dict[row['ver']] = []
        v_dict[row['ver']].append(row['title'])
        pass

    books = v_dict.pop(kwargs['ver'])
    for b in books:
        print(kwargs['ver'], "\t", b)
        continue

    print()
    for v, bl in v_dict.items():
        print(v, "\t有%s个记录" % len(bl))

    return


@cli.command()
@click.option('--title', '-t', required=True, type=click.STRING, help='小说名称')
@click.option('--ver', '-v', default='修订版', help='版本', show_default=True)
@click.pass_context
def dump_book(ctx, **kwargs):
    """导出电子书"""
    import config.db
    from jinja2 import PackageLoader, Environment
    import bson
    c0 = config.db.connect()
    c1 = config.db.connect_contents()
    env = Environment(loader=PackageLoader(__name__, 'templates'))

    book = c0.find_one({'title': kwargs['title'], 'ver': kwargs['ver']})
    catalog = book['catalog']
    tpl = env.get_template('index.html')
    html = tpl.render(title=book['title'], ver=book['ver'], catalog=catalog)
    with open('data/index.html', 'w') as out_index:
        out_index.write(html)

    tpl_chapter = env.get_template('chapter.html')

    for cat in catalog:
        body_id = cat['body_id']
        doc = c1.find_one({'_id': bson.ObjectId(body_id)})
        html_chapter = tpl_chapter.render(title=book['title'] + " " + cat['title'],
                                          body=doc['body'])
        with open('data/pages/%s.html' % body_id, 'w') as out_body:
            out_body.write(html_chapter)
        pass


pass

if __name__ == '__main__':
    cli()

    pass
