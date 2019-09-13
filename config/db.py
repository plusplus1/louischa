#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo

_connection_string = "mongodb://localhost:27017/jinyongwang"
_database = "jinyongwang"
_table = "novels"
_table_content = "contents"
_client = None


def connect(table=None):
    global _client
    if not _client:
        _client = pymongo.MongoClient(_connection_string)
    db = _client.get_database(_database)

    if table:
        return db.get_collection(table)
    else:
        return db.get_collection(_table)


def connect_contents():
    return connect(_table_content)
