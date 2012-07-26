#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "virtualenv.bundle"))
sys.path.append(os.path.join(os.getcwd(), "flaskcommon"))

from flask import Flask
from werkzeug import import_string

from flaskcommon.config import configure_app
from flaskcommon.extensions import create_app_database, db, cache
from flaskcommon.log import configure_logging

from flaskbbs.admin import configure_admin

__all__ = ["create_app"]

DEFAULT_APP_NAME = "flaskbbs"

BUILTIN_BLUEPRINTS = [
    ("flaskcommon.auth", "blueprint_auth", "/auth"),
    ("flaskcommon.message", "bp_message", "/message"),
]

BLUEPRINTS = [
    ("flaskbbs.apps.frontend", "bp_frontend"),
    ("flaskbbs.apps.bbs", "bp_bbs", "/bbs"),
]

def create_app(config=None, app_name=None, modules=None):
    if app_name is None:
        app_name = DEFAULT_APP_NAME

    app = Flask(app_name, static_folder='../static')

    configure_app(app, config)
    configure_logging(app)
    configure_debug(app)

    configure_errorhandlers(app)
    configure_extensions(app)
    configure_before_handlers(app)
    configure_template_filters(app)
    configure_context_processors(app)
    # configure_after_handlers(app)
    configure_admin(app)

    init_flaskcommon(app)
    register_blueprints(app)

    # create database & tables, insert some default records.
    #init_database(app)

    return app

def configure_errorhandlers(app):
    pass

def configure_extensions(app):
    db.app = app
    db.init_app(app)

    cache.init_app(app)

    from flaskcommon.auth.views import login_manager_init
    login_manager_init(app)

def configure_before_handlers(app):
    pass

def configure_template_filters(app):
    pass

def configure_debug(app, debug=None, debug_toolbar=None):
    if debug == None:
        debug = app.config.get("DEBUG", False)
    if debug_toolbar == None:
        debug_toolbar = app.config.get("DEBUG_TOOLBAR", False)

    app.debug = debug
    if debug_toolbar:
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            DebugToolbarExtension(app)
        except:
            print "debugtoolbar setup failed!\n"

def configure_context_processors(app):
    pass

def init_flaskcommon(app):
    for blueprint in BUILTIN_BLUEPRINTS:
        __register_blueprint(app, blueprint)

def register_blueprints(app):
    for blueprint in BLUEPRINTS:
        __register_blueprint(app, blueprint)

def __register_blueprint(app, blueprint):
    path = ""
    name = ""
    url_prefix = None
    if type(blueprint) == "":
        path = blueprint
        name = "bp_" + blueprint.split(".")[-1]
    else:
        path = str(blueprint[0])
        if len(blueprint) >= 2:
            name = str(blueprint[1])
        if len(blueprint) >= 3:
            url_prefix = str(blueprint[2])
    try:
        package = import_string(path+".views")
    except:
        raise

    bp = getattr(package, name, None)
    if not bp:
        app.logger.error("import blueprint %s from %s failed!\n" %(name, package+".views"))
        raise

    if url_prefix:
        if not url_prefix.startswith("/"):
            url_prefix = "/" + url_prefix
        app.register_blueprint(bp, url_prefix=url_prefix)
    else:
        app.register_blueprint(bp)

def __init_blueprint_data(app, blueprint):
    path = ""
    name = ""
    url_prefix = None
    if type(blueprint) == "":
        path = blueprint
    else:
        path = str(blueprint[0])

    try:
        models = import_string(path + ".models")
    except:
        app.logger.error("cannot import module %s, or module %s do not have models.py file. blueprint: %s\n" %(path, path, blueprint))
        return

    if hasattr(models, "init_data"):
        models.init_data(app)

def init_database(app):
    create_app_database(app)
    with app.test_request_context():
        for blueprint in BUILTIN_BLUEPRINTS + BLUEPRINTS:
            __init_blueprint_data(app, blueprint)

if __name__ == '__main__':
    app = create_app()
    app.run()
