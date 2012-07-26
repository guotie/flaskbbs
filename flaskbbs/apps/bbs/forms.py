#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

from models import Section, Node, Topic

from flask.ext.wtf import Form, TextField, BooleanField, TextAreaField
from flask.ext.wtf import URL, Required, Optional, Email, Regexp, EqualTo, Length, ValidationError

from flaskcommon.utils.wtforms_extended_selectfield import SelectWidget, SelectField
from flask.ext.admin.form import ChosenSelectWidget
from wtforms.ext.sqlalchemy.fields import QuerySelectField

class TopicForm(Form):
    node = SelectField(u'节点', validators=[Required()], widget=SelectWidget())
    title = TextField(u"标题", validators=[Required(), Length(max=64)])
    content = TextAreaField(u"内容", description=u"支持Markdown语言", validators=[Required()])
    tags = TextField(u'标签', description=u'多个标签用，分割', validators=[Length(max=100)])

class NodeForm(Form):
    section = QuerySelectField(u"Section", validators=[Required()], widget=ChosenSelectWidget())
    node_name = TextField(u"节点名称", validators=[Required(), Length(max=40)])
    node_title = TextField(u"节点标题", validators=[Required(), Length(max=100)])
    descp = TextAreaField(u"节点介绍", validators=[Length(max=600)])
    item_per_page = SelectField(u"每页条数", choices=[(10, '10'), (20, '20'), (30, '30'), (40, '40'), (50, '50'), (100, '100')],
                        coerce=int, default=30)

    header = TextAreaField(u"头部html", validators=[Length(max=800)])
    footer = TextAreaField(u"底部html", validators=[Length(max=800)])
    sidebar = TextAreaField(u"侧栏html", validators=[Length(max=800)])
    sidebar_ads = TextAreaField(u"侧栏广告", validators=[Length(max=800)])

    avatar_url = TextField(u"节点头像", validators=[Length(max=200)])

class ReplyForm(Form):
    content = TextAreaField(u"回复", validators=[Required()], description=u"支持Markdown语言")
