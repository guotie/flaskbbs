#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

from flaskcommon.auth.models import User

from flaskcommon.extensions import db

from flask.ext.sqlalchemy import BaseQuery

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class MessageQuery(BaseQuery):
    def messages(self, recv_id):
        '''
        all user recv messages
        '''
        return self.filter(Message.direction==0).filter(Message.receiver_id==recv_id).order_by(Message.send_tm.desc())

    def send_messages(self, send_id):
        return self.filter(Message.direction==1).filter(Message.sender_id==send_id)

class Message(db.Model):
    __tablename__ = "message"

    query_class = MessageQuery

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    sender_id = db.Column(db.Integer, ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, ForeignKey('user.id'))
    direction = db.Column(db.Integer, default=0)
    reply_id = db.Column(db.Integer, default=0)
    ancestor_id = db.Column(db.Integer, default=0)

    send_tm = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, default=0)

    sender = relationship("User", primaryjoin="Message.sender_id==User.id")
    receiver = relationship("User", primaryjoin="Message.receiver_id==User.id")

def create_message(sender_id, recv, title, content, reply_id=0, backup=False):
    m1 = Message(title=title, content=content, sender_id=sender_id, receiver_id=recv.id, direction=0, reply_id=reply_id,
        send_tm=datetime.now(), status=0)
    if reply_id:
        reply = Message.query.get(reply_id)
        m1.ancestor_id = reply.ancestor_id
    if backup:
        m2 = Message(title=title, content=content, sender_id=sender_id, receiver_id=recv.id, direction=1, reply_id=reply_id,
            send_tm=datetime.now(), status=0)
        db.session.add([m1, m2])
    else:
        db.session.add(m1)

    db.session.commit()

    return m1
