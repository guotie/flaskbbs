#!/usr/bin/python
# -*- coding: utf-8 -*-
#
__author__ = 'guotie'

import datetime
import urllib

from flask import g, request, redirect, session, flash, url_for
from flask import render_template

from flask import Flask, Blueprint
bp_message = Blueprint('message', __name__, template_folder='templates', static_folder='static')

from flaskcommon.auth.models import User
from flaskcommon.utils import generate_url, get_page_query

from flask.ext.login import current_user, login_required

from models import Message, create_message
from forms import SendMessageForm, SendToMessageForm
from flask.ext.wtf import TextField

@bp_message.route('/')
@login_required
def index():
    page = request.args.get('page', 0, type=int)
    query = Message.query.messages(current_user.id)
    count, num_pages, messages = get_page_query(query, page, page_size=10)

    def pager_url(p):
        return generate_url('.index', p)
    return render_template("message.html",
                            messages=messages,
                            count=count,
                            pager_url=pager_url,
                            num_pages=num_pages,
                            page=page)

@bp_message.route('/sendto', methods=['GET', 'POST'])
@login_required
def sendto():
    form = SendToMessageForm(request.form)
    if request.method == 'POST' and form.validate():
        receiver = User.query.get_by_username(form.data['recv'].strip())
        if receiver:
            msg = create_message(sender_id=current_user.id, recv=receiver, title=form.data['title'], content=form.data['content'])
            return render_template("send_ok.html", msg=msg)
        form.recv.errors.append(u'用户名不存在！')
    return render_template("send_message.html", form=form, actionurl=url_for(".sendto"))

@bp_message.route('/send/<recv>', methods=['GET', 'POST'])
@login_required
def send(recv):
    form = SendMessageForm(request.form)
    _recv = urllib.unquote(recv)
    receiver = User.query.filter(User.username==_recv.strip()).first()
    if not receiver:
        flash(u'未知用户%s' %_recv)
        return redirect(url_for(".sendto") or '/')
    if request.method == 'POST' and form.validate():
        msg = create_message(sender_id=current_user.id, recv=receiver, title=form.data['title'], content=form.data['content'])
        return render_template("send_ok.html", msg=msg)
    return render_template("send_message.html", form=form, actionurl=url_for(".send", recv=recv))

@bp_message.route('/reply', methods=['GET', 'POST'])
@login_required
def reply():
    return render_template("reply.html")
