#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask.globals import g

__author__ = 'guotie'

from flask.ext.sqlalchemy import SQLAlchemy
from flaskext.cache import Cache

__all__ = ['db', 'cache']

class nullpool_SQLAlchemy(SQLAlchemy):
    def apply_driver_hacks(self, app, info, options):
        super(nullpool_SQLAlchemy, self).apply_driver_hacks(app, info, options)
        from sqlalchemy.pool import NullPool
        options['poolclass'] = NullPool
        #print options, info
        try:
            del options['pool_size']
        except:
            pass

db = nullpool_SQLAlchemy()
cache = Cache()

def create_app_database(app):
    with app.test_request_context():
        db.drop_all(app=app)
        db.create_all(app=app)
