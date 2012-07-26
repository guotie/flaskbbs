#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

import os

class SaeProductionConfig(object):
    DEBUG = True
    TESTING = False
    DEBUG_TOOLBAR = False
    import sae.core
    info = sae.core.Application()
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%d/%s' %(info.mysql_user, info.mysql_pass, info.mysql_host, int(info.mysql_port), info.mysql_db)
    SECRET_KEY = info.secret_key
    ACCESS_KEY = info.access_key

def configure_app(app, config):
    if config:
        app.config.from_pyfile(os.path.join(os.getcwd(), config))
    else:
        app.config.from_pyfile(os.path.join(os.getcwd(), "default.cfg"))

    app.config.from_envvar('FLASK_BBS_CONFIG', silent=True)

    if app.config.get("PLATFORM", "") == "sae":
        app.config.from_object(SaeProductionConfig)
