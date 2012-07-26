#!/usr/bin/python
# -*- coding: utf-8 -*-
#
__author__ = 'guotie'

from flaskcommon.config import MCACHE

if MCACHE == 0:
    from .memcache import mc as mcache
elif MCACHE == 1:
    from .kvdb import kv as mcache
elif MCACHE == 2:
    from localcache import lc as mcache
else:
    mcache = None
    raise NotImplementedError

def mcache_get(key):
    return mcache.get(key)

def mcache_set(key, value, expires_in = 0, min_compress_len = 0):
    return mcache.set(key, value, expires_in, min_compress_len)

def mcahce_delete(key, time=0):
    return mcache.delete(key, time)

def mcahce_get_multi(keys, key_prefix=None):
    return mcahce.get_multi(keys, key_prefix)

def mcache_set_multi(mapping, time=0, key_prefix=None):
    return mcache.set_multi(mapping, time, key_prefix)

def mcache_delete_multi(keys, time=0, key_prefix=None):
    return mcache.delete_multi(keys, time, key_prefix)

def mcache_incr(key, delta=1):
    return mcache.incr(key, delta)

def mcache_decr(key, delta=1):
    return mcache.decr(key, delta)
