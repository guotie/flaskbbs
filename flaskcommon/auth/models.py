#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

import hashlib
import urllib

from datetime import datetime
from random import choice

from flaskcommon.extensions import db, cache
#from flaskcommon.config.appinfo import SECRET_KEY

from flask import url_for, current_app

from flask.ext.sqlalchemy import BaseQuery

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from flask.ext.login import AnonymousUser, UserMixin

class UserQuery(BaseQuery):
    def from_identity(self, identity):
        """
        Loads user from flaskext.principal.Identity instance and
        assigns permissions from user.

        A "user" instance is monkeypatched to the identity instance.

        If no user found then None is returned.
        """

        try:
            user = self.get(int(identity.name))
        except ValueError:
            user = None

        if user:
            identity.provides.update(user.provides)

        identity.user = user

        return user

    def search(self, key):
        query = self.filter(db.or_(User.auth_id==key,
            User.nickname.ilike('%'+key+'%'),
            User.username.ilike('%'+key+'%')))
        return query

    def get_by_username(self, username):
        user = self.filter(User.username==username).first()
        return user

    def get_by_authid(self, auth_id):
        user = self.filter(User.auth_id==auth_id).first()
        #if user is None:
        #    abort(404)
        return user

class User(UserMixin, db.Model):
    __tablename__ = "user"

    query_class = UserQuery

    id = db.Column(db.Integer, primary_key=True)
    # which is provided by sina weibo, qq weibo, twitter, facebook, etc
    auth_id = db.Column(db.String(32), unique=True, nullable=False)
    username = db.Column(db.String(32), unique=True)
    nickname = db.Column(db.String(32), nullable=True)
    modify_chance = db.Column(db.Integer, default=3)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(64), nullable=True)
    activation_key = db.Column(db.String(64), nullable=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    block = db.Column(db.Boolean, default=False)
    avater = db.Column(db.String(200), nullable=True)
    avater_s = db.Column(db.String(200), nullable=True)
    avater_l = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(12), default='', nullable=True)

    vest = db.Column(db.Boolean, default=False)
    vest_accounts = db.Column(db.Integer, default=0)

    profile = relationship("UserProfile", uselist=False, backref="user")

    # Required for administrative interface
    def __unicode__(self):
        return self.username

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.profile = None

    def is_active(self):
        return self.block == False

    def is_superuser(self):
        return self.id == 1

    @property
    def url(self):
        return url_for("auth.member", username=urllib.quote(self.username))

    @classmethod
    def create_password(cls, raw):
        salt = User.create_token(8)
        hsh = hashlib.sha1(salt + raw + current_app.config["SECRET_KEY"]).hexdigest()
        return "%s$%s" % (salt, hsh)

    @classmethod
    def create_token(cls, length=16):
        chars = ('0123456789'
                 'abcdefghijklmnopqrstuvwxyz'
                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        salt = ''.join([choice(chars) for i in range(length)])
        return salt

    def check_password(self, raw):
        if '$' not in self.password:
            return False
        salt, hsh = self.password.split('$')
        verify = hashlib.sha1(salt + raw + current_app.config["SECRET_KEY"]).hexdigest()
        return verify == hsh

class UserProfileQuery(BaseQuery):
    def get_profile(self, user):
        try:
            prof = self.get(int(user.id))
        except:
            prof = None

        return prof

class UserProfile(db.Model):
    __tablename__ = "userprofile"

    query_class = UserProfileQuery

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))

    role = db.Column(db.Integer, default=0)

    friends = db.Column(db.Integer, default=0)
    followings = db.Column(db.Integer, default=0)
    fans = db.Column(db.Integer, default=0)
    nodes = db.Column(db.Integer, default=0)

    topics = db.Column(db.Integer, default=0)
    replies = db.Column(db.Integer, default=0)

    city = db.Column(db.String(40), nullable=True)
    province = db.Column(db.String(40), nullable=True)
    birthday = db.Column(db.Date, nullable=True)
    blog = db.Column(db.String(100), nullable=True)
    descp = db.Column(db.String(500), nullable=True)
    signature = db.Column(db.String(200), nullable=True)
    workat = db.Column(db.String(200), nullable=True)
    realname = db.Column(db.String(80), nullable=True)
    idcard = db.Column(db.String(32), nullable=True)

    # money
    copper_coins = db.Column(db.BigInteger, default=0)
    gold_coins = db.Column(db.BigInteger, default=0)

    reputation = db.Column(db.Integer, default=100)
    favourate = db.Column(db.Integer, default=0)

    messages = db.Column(db.Integer, default=0)
    unread = db.Column(db.Integer, default=0)

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)

    # Required for administrative interface
    def __unicode__(self):
        return "User's %d profile" %self.id

class Anonymous(AnonymousUser):
    username = u"Anonymous"

def create_user(auth_id, name, email, password=None, copper_coins=200, **kw1):
    user = User(auth_id=auth_id, username=name, email=email, **kw1)
    if password:
        user.password = User.create_password(password)

    profile = UserProfile(copper_coins=copper_coins)
    user.profile=profile
    user.avater = "/static/image/default_avatar.png"

    db.session.add_all([user, profile])
    db.session.commit()
    return user

def init_data(app):
    create_user(auth_id="local_admin", name="admin", email="admin@example.com", password="flaskbbs")
