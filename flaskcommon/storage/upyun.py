#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'
from . import StorageBase, StorageManagerBase

from flask import current_app
from flaskcommon.utils.upyun import UpYun

class Storage(StorageBase):
    '''
    Storage of upyun
    '''
    def __init__(self, path):
        self.client = UpYun(bucket=current_app.config["upyun_bucket"],
                        username=current_app.config["upyun_username"],
                        password=current_app.config["upyun_password"])

        super(self).__init__(self, path)

    def save(self, name, content, callback=None):
        self.upyun.writeFile(name, content)
        if callback:
            callback(self.client.bucket + name)

class StorageManager(StorageManagerBase):
    '''
    StorageManager of upyun
    '''