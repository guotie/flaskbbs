#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

from flask import redirect, url_for

from flask import Blueprint
bp_frontend = Blueprint('bp_frontend', __name__)

@bp_frontend.route('/')
def index():
    return redirect(url_for("bp_bbs.bbs_index"))
