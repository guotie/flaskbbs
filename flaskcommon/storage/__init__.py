#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

from __future__ import absolute_import, division

class StorageBase(object):
    def __init__(self, path):
        self.path = path

    def save(self, name, content, callback=None):
        raise NotImplementedError

class StorageManagerBase(object):
    '''Manage multi StorageBase
    '''
    def __init__(self, prefix, root_path):
        self.prefix = prefix
        self.root_path = root_path
        self.storages = {}
