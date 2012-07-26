#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

from flask.ext.wtf import Form, TextField, BooleanField, TextAreaField
from flask.ext.wtf import URL, Required, Optional, Email, Regexp, EqualTo, Length, ValidationError

from models import Message

class SendMessageForm(Form):
    title = TextField(u"标题", validators=[Required(), Length(max=50)])
    content = TextAreaField(u"内容", validators=[Required(), Length(max=500)])

class SendToMessageForm(Form):
    recv = TextField(u"收件人", validators=[Required(), Length(max=50)])
    title = TextField(u"标题", validators=[Required(), Length(max=50)])
    content = TextAreaField(u"内容", validators=[Required(), Length(max=500)])
