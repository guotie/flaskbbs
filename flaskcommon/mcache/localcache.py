#!/usr/bin/python
# -*- coding: utf-8 -*-
#
__author__ = 'guotie'

class LocalCache(dict):
    def __init__(self):
        self.d = {}

    def get(self, key):
        try:
            return self.d[key]
        except:
            return None

    def set(self, key, value, expires_in = 0, min_compress_len = 0):
        self.d[key] = value

    def delete(self, key, time=0):
        try:
            del self.d[key]
        except:
            pass

    def get_multi(self, keys, key_prefix=None):
        pass

    def set_multi(mapping, time=0, key_prefix=None):
        pass

    def delete_multi(keys, time=0, key_prefix=None):
        pass

    def incr(key, delta=1):
        pass

    def decr(key, delta=1):
        pass

lc = LocalCache()
