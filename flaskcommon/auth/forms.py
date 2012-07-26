#!/usr/bin/python
# -*- coding: utf-8 -*-
#
__author__ = 'guotie'

from flask.ext.wtf import Form, TextField, BooleanField, TextAreaField, SelectField
from flask.ext.wtf import IntegerField, FileField, PasswordField,RadioField, DateField
from flask.ext.wtf import URL, Required, Optional, Email, Regexp, EqualTo, Length, ValidationError

from wtforms.widgets.core import HTMLString, ListWidget, TextInput
from models import User

from flask.ext.login import login_user
#from flaskcommon.mcache import mcache_set

from flask.ext.admin.form import DatePickerWidget

import re, datetime

re_username = re.compile(u"^([\u4E00-\u9FFF]|[a-zA-Z0-9-_\.]){1,32}$")
re_avater = re.compile("^[^/\\\\]\.jpg$")

reserved_words = (u"administrator", u"root", u"admin", u"管理员", u"版主", u"超级版主", u"系统管理员", u"编辑", u"user", u"superuser", u'system')

class BSListWidget(ListWidget):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        #html = [u'<%s %s>' % (self.html_tag, html_params(**kwargs))]
        html = []
        for subfield in field:
            html.append(u'<label class="radio inline"> %s %s </label>' %(subfield(), subfield.label.text))

        #html.append(u'</%s>' % self.html_tag)
        return HTMLString(u''.join(html))

class DisabledTextInput(TextInput):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        return HTMLString(u'<input %s disabled>' % self.html_params(name=field.name, **kwargs))

class UserRegForm(Form):
    name = TextField(u"用户名", validators=[Required(), Length(min=3, max=32), Regexp(re_username)])
    email = TextField(u'Email', validators=[Required(), Email()])
    gender = RadioField(u'性别', coerce=int, choices=[(0, u'男'), (1, u'女')], default=0, widget=BSListWidget())
    password = PasswordField(u'密码', validators=[Required(), Length(min=5,max=60), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField(u'确认密码', validators=[Required(), Length(min=5,max=60)])

    def validate_name(form, field):
        name = field.data.lower()
        if name in reserved_words:
            raise ValidationError(u'用户名不能为系统保留字')
        user = User.query.filter(User.username==field.data).first()
        if user:
            raise ValidationError(u'该用户名已被注册')

    def validate_email(form, field):
        user = User.query.filter(User.email==field.data).first()
        if user:
            raise ValidationError(u'该email已被注册')

class LoginForm(Form):
    email = TextField(u'用户名或Email', validators=[Required()])
    password = PasswordField(u'密码', validators=[Required(), Length(min=5,max=60)])


class SettingsForm(Form):
    username = TextField(u'用户名', validators=[Required(), Length(min=4, max=32), Regexp(re_username)])
    #nickname = TextField(u'昵称', validators=[Optional(), Length(max=32)])
    city = TextField(u'城市', validators=[Optional(), Length(max=40)])
    province = TextField(u'省份', validators=[Optional(), Length(max=40)])
    birthday = DateField(u'出生年月日', validators=[Optional()], widget=DatePickerWidget(), default=datetime.date(1990,1,1))
    blog = TextField(u'博客', validators=[Optional(), URL(), Length(max=100)])
    descp = TextAreaField(u'个人介绍', validators=[Optional(), Length(max=500)])
    signature = TextAreaField(u'签名', validators=[Optional(), Length(max=200)])
    realname = TextField(u'真实姓名', validators=[Optional(), Length(max=80)])
    idcard = TextField(u'身份证', validators=[Optional(), Length(max=32)])

def settings_from_user(user):
    profile = user.profile

    form = SettingsForm(username=user.username, nickname=user.nickname, city=profile.city,
                        province=profile.province, blog=profile.blog, descp=profile.descp, birthday=profile.birthday,
                        signature=profile.signature, realname=profile.signature, idcard=profile.idcard)
    if user.modify_chance <= 0:
        form.username.widget = DisabledTextInput()
        form.username.extra_class = "disabled"
    return form

class ChangePasswordForm(Form):
    old_password = PasswordField(u'旧密码', validators=[Required(), Length(min=5,max=60)])
    new_password = PasswordField(u'新密码', validators=[Required(), Length(min=5,max=60), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField(u'确认一次新密码', validators=[Required(), Length(min=5,max=60)])

class FindPasswordForm(Form):
    email = TextField(u'Email', validators=[Required(), Email()])

class AvaterForm(Form):
    avater = FileField(u'头像', validators=[Required(), Regexp(re_avater)])
