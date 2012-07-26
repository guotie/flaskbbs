#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

from . import StorageBase, StorageManagerBase
from flask import current_app

import sae.storage

class Storage(StorageBase):
    '''
    Storage of sae
    '''
    def __init__(self, path):
        self.client = sae.storage.Client()
        super(self).__init__(self, path)

    def save(self, name, content, callback=None):
        ob = sae.storage.Object(content)
        self.client.put(current_app.config["sae_storage_domain"], name, content)

class StorageManager(StorageManagerBase):
    '''
    StorageManager of sae
    '''