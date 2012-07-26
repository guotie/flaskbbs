#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

from . import StorageBase, StorageManagerBase

from __future__ import absolute_import, division

import os
import errno
import shutil

class Storage(StorageBase):
    '''
    Storage of local file system
    '''
    @classmethod
    def save(cls, name, content, callback=None):
        path = os.path.join(os.path.join(os.getcwd(), "_data"), name)
        f = open(path, 'w')
        f.write(content)
        f.close()
        if not callback:
            return
        callback(path)
        return

class StorageManager(StorageManagerBase):
    '''
    StorageManager of local file system
    '''