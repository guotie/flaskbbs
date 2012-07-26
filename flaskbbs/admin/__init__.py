#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

try:
    from flask.ext.sqlalchemy import SQLAlchemy
    from flask.ext import wtf
    from flask.ext.admin import Admin, expose, AdminIndexView
    from flask.ext.admin.contrib import sqlamodel
    from flask.ext.admin.contrib.sqlamodel import filters
    from flask.ext.login import current_user
except:
    raise

from flask import flash

from flaskcommon.extensions import db, cache
from flaskcommon.auth.models import User, UserProfile
from flaskbbs.apps.bbs.models import Section, Node, Topic, Reply

class AuthView(sqlamodel.ModelView):
    def is_accessible(self):
        return current_user.is_authenticated() and current_user.is_superuser()

class HomeAdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated() and current_user.is_superuser()

class UserAdmin(AuthView):
    '''
    User model's admin
    '''

    # Visible columns in the list view
    #list_columns = ('title', 'user')
    excluded_list_columns = ['activation_key', 'avatar']
    # List of columns that can be sorted. For 'user' column, use User.username as
    # a column.
    sortable_columns = ('id', 'username', 'date')

    # Rename 'title' columns to 'Post Title' in list view
    rename_columns = dict(auth_id='3rd auth id')

    searchable_columns = ('username',)

    column_filters = ('username',
                      'gender',
                      'date_joined')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(UserAdmin, self).__init__(User, session, **kwargs)

class UserProfileAdmin(AuthView):
    '''UserProfile model's admin
    '''
    # Disable model creation
    can_create = False
    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(UserProfileAdmin, self).__init__(UserProfile, session, **kwargs)

def configure_admin(app):
    admin = Admin(app, index_view=HomeAdminView())
    admin.add_view(UserAdmin(db.session, name="User", endpoint="user", category="Auth"))
    admin.add_view(UserProfileAdmin(db.session, name="UserProfile", endpoint="profile", category="Auth"))

    admin.add_view(AuthView(Section, db.session, name="Section", endpoint="section", category="BBS"))
    admin.add_view(AuthView(Node, db.session, name="Node", endpoint="node", category="BBS"))
    admin.add_view(AuthView(Topic, db.session, name="Topic", endpoint="topic", category="BBS"))
    admin.add_view(AuthView(Reply, db.session, name="Reply", endpoint="reply", category="BBS"))
