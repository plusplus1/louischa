#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo

_connection_string = "mongodb://localhost:27017/jinyongwang"
_database = "jinyongwang"
_table = "novels"

_client = None


def connect():
    global _client
    if not _client:
        _client = pymongo.MongoClient(_connection_string)
    db = _client.get_database(_database)
    return db.get_collection(_table)
