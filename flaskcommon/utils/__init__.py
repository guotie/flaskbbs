#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

from flask import url_for
from copy import deepcopy

from flaskcommon.extensions import cache

import datetime

def generate_url(view=None, page=None, sort=None, sort_desc=None,
                 search=None, filters=None, **args):
    """code from flask-admin

        Generate page URL with current page, sort column and
        other parameters.

        `view`
            View name
        `page`
            Page number
        `sort`
            Sort column index
        `sort_desc`
            Use descending sorting order
        `search`
            Search query
        `filters`
            List of active filters
    """
    if not search:
        search = None

    if not page:
        page = None

    if args:
        kwargs=deepcopy(args)
        kwargs.update(page=page, sort=sort, desc=sort_desc, search=search)
    else:
        kwargs = dict(page=page, sort=sort, desc=sort_desc, search=search)

    if filters:
        for i, flt in enumerate(filters):
            key = 'flt%d_%d' % (i, flt[0])
            kwargs[key] = flt[1]

    return url_for(view, **kwargs)

@cache.memoize(timeout=10)
def get_page_query(query, page=None, page_size=10, execute=True):
    count = query.count()
    # Pagination
    if page is not None:
        query = query.offset(page * page_size)

    query = query.limit(page_size)
    if execute:
        query = query.all()

    num_pages = count / page_size
    if count % page_size:
        num_pages += 1

    return count, num_pages, query

def timesince(value, locale='en_US'):
    now = datetime.datetime.now()
    delta = now - value
    if delta.days > 365:
        return u'%s 年前' % (delta.days / 365)
    if delta.days > 30:
        return u'%s 月前' % (delta.days / 30)
    if delta.days > 0:
        return u'%s 日前' % delta.days
    if delta.seconds > 3600:
        return u'%s 小时前' % (delta.seconds / 3600)
    if delta.seconds > 60:
        return u'%s 分钟前' % (delta.seconds / 60)
    return u'刚刚'
